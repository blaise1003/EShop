from decimal import Decimal
from django.contrib.auth.models import Group, User
from django.db import models
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from product import signals
from product.models import Product
from product.prices import PriceAdjustment, PriceAdjustmentCalc
from satchmo_utils.fields import CurrencyField
from threaded_multihost import threadlocals
import datetime
import logging

log = logging.getLogger('tieredpricing.models')

class PricingTierManager(models.Manager):

    def by_user(self, user):
        """Get the pricing tiers for a user"""
        key = 'TIER_%i' % user.id
        current = threadlocals.get_thread_variable(key)

        if current is None:
            groups = user.groups.all()
            current = []
            if groups and not user.is_superuser and not user.is_staff:
                filterQ = Q()
                for group in groups:
                    filterQ = filterQ | Q(group=group)
                current = list(self.filter(filterQ))

            threadlocals.set_thread_variable(key, current)

        if not current:
            raise PricingTier.DoesNotExist

        return current

class PricingTier(models.Model):
    """A specific pricing tier, such as "trade customers"
    """
    group = models.OneToOneField(Group, help_text=_(u'The user group that will receive the discount'))
    title = models.CharField(_(u'Title'), max_length=50)
    discount_percent = models.DecimalField(_(u"Discount Percent"), null=True, blank=True,
        max_digits=5, decimal_places=2,
        help_text=_(u"This is the discount that will be applied to every product if no explicit Tiered Price exists for that "
                    u"product.  Leave as 0 if you don't want any automatic discount in that case."))

    objects = PricingTierManager()

    def __unicode__(self):
        return self.title

class TieredPriceManager(models.Manager):

    def by_product_qty(self, tier, product, qty=Decimal('1')):
        """Get the tiered price for the specified product and quantity. If it's a product variation, we check the parent too"""

        qty_discounts = list(product.tieredprices.exclude(expires__isnull=False, expires__lt=datetime.date.today()). \
                filter(quantity__lte=qty, pricingtier=tier).order_by('-quantity'))
        if qty_discounts:
            # Get the price with the quantity closest to the one specified without going over
            return qty_discounts[0]

        # If we haven't found a price, see if the parent product has a price tier
        if 'ProductVariation' in product.get_subtypes():
            parent_product = product.productvariation.parent.product
            qty_discounts = list(parent_product.tieredprices.exclude(expires__isnull=False, expires__lt=datetime.date.today()). \
                    filter(quantity__lte=qty, pricingtier=tier).order_by('-quantity'))
            if qty_discounts:
                # Get the price with the quantity closest to the one specified without going over
                return qty_discounts[0]
        raise TieredPrice.DoesNotExist

class TieredPrice(models.Model):
    """
    A Price which applies only to special tiers.
    """
    pricingtier = models.ForeignKey(PricingTier, related_name="tieredprices")
    product = models.ForeignKey(Product, related_name="tieredprices")
    price = CurrencyField(_(u"Price"), max_digits=14, decimal_places=6, )
    quantity = models.DecimalField(_(u"Discount Quantity"), max_digits=18, decimal_places=6,  default='1', help_text=_(u"Use this price only for this quantity or higher"))
    expires = models.DateField(_(u"Expires"), null=True, blank=True)

    objects = TieredPriceManager()

    def _dynamic_price(self):
        """Get the current price as modified by all listeners."""
        adjust = PriceAdjustmentCalc(self)
        signals.satchmo_price_query.send(self, adjustment=adjust,
            slug=self.product.slug, discountable=self.product.is_discountable)
        return adjust.final_price()

    dynamic_price = property(fget=_dynamic_price)

    def save(self, **kwargs):
        """Save with the prevention of storing duplicates""" 
        prices = TieredPrice.objects.filter(product=self.product, quantity=self.quantity, pricingtier=self.pricingtier)
        if self.expires:
            prices = prices.filter(expires=self.expires)
        else:
            prices = prices.filter(expires__isnull=True)
        if self.id:
            prices = prices.exclude(id=self.id)
        if prices.count():
            return #Duplicate Price

        super(TieredPrice, self).save(**kwargs)

    class Meta:
        ordering = ['pricingtier', 'expires', '-quantity']
        verbose_name = _("Tiered Price")
        verbose_name_plural = _("Tiered Prices")
        unique_together = (("pricingtier", "product", "quantity", "expires"),)

def tiered_price_listener(signal, adjustment=None, **kwargs):
    """Listens for satchmo_price_query signals, and returns a tiered price instead of the
    default price.

    Requires threaded_multihost.ThreadLocalMiddleware to be installed so
    that it can determine the current user."""

    if kwargs.has_key('discountable'):
        discountable = kwargs['discountable']
    else:
        discountable = adjustment.product.is_discountable

    if discountable:
        product = adjustment.product
        user = threadlocals.get_current_user()
        if user and not user.is_anonymous():
            try:
                tiers = PricingTier.objects.by_user(user)
                log.debug('got tiers: %s', tiers)
                best = None
                besttier = None
                currentprice = adjustment.final_price()
                qty = adjustment.price.quantity
                for tier in tiers:
                    candidate = None
                    try:
                        tp = TieredPrice.objects.by_product_qty(tier, product, qty)
                        log.debug("Found a Tiered Price for %s qty %d = %s", product.slug, qty, tp.price)
                        candidate = tp.price
                    except TieredPrice.DoesNotExist:
                        pcnt = tier.discount_percent
                        if pcnt is not None and pcnt != 0:
                            candidate = currentprice * (100-pcnt)/100

                    if best is None or (candidate and candidate < best):
                        best = candidate
                        besttier = tier

                        log.debug('best = %s', best)

                if best is not None:
                    delta = currentprice - best
                    adjustment += PriceAdjustment(
                        'tieredpricing',
                        _('Tiered Pricing for %(tier)s' % { 'tier': besttier.group.name}),
                        delta)

            except PricingTier.DoesNotExist:
                pass

# dispatch_uid prevents applying the same discount multiple times if the module is imported repeatedly.
signals.satchmo_price_query.connect(tiered_price_listener, dispatch_uid='tieredpricing.models.tiered_price_listener')

def pricingtier_group_change_listener(action=None, reverse=None, instance=None, **kwargs):
    """Listens for changes of m2m relation between auth.User/Group and resets related threadlocals cached object"""
    if action in ('post_add', 'pre_remove', 'pre_clear'):
        if not reverse:
            modified_users_id = [instance.id]
        else:
            modified_users_id = [u.id for u in instance.user_set.all()]
            # After required Django version will be 1.3+, the previous line can be replaced by:
            #modified_users = kwargs['pk_set']
        for user_id in modified_users_id:
            key = 'TIER_%i' % user_id
            threadlocals.set_thread_variable(key, None)

models.signals.m2m_changed.connect(pricingtier_group_change_listener, sender=User.groups.through)
