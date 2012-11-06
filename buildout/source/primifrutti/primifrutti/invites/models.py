# -*- coding: utf-8 -*-
from uuid import uuid1
from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from livesettings import config_value
from l10n.utils import moneyfmt
from satchmo_utils.fields import CurrencyField
from product.models import (DISCOUNT_SHIPPING_CHOICES,
    Discount, Product, Category)
from satchmo_store.mail import send_store_mail
from satchmo_store.shop.models import Config
from satchmo_store.contact.models import Contact


class InvitesManager(models.Manager):
    """Manages invites.

    Allows to create them, to do smart retrievals, and to reset ones sent by
    specific inviters.
    """

    def get_by_code(self, code, site=None):
        """Gets the invite (given the code) or raises ``Invite.DoesNotExist``
        """
        if site is None:
            site = Site.objects.get_current()
        return self.all().get(code__exact=code, site=site,
                              used=False, countable=True)

    def create(self, user, recipient, recipient_name, recipient_surname,
               text=None, site=None):
        """Creates a new invite.

        Use this and don't instantiate ``Invite`` classes directly and then
        save them, as this will not send any mail.
        """
        if site is None:
            site = Site.objects.get_current()
        invites_sent = self.all().filter(
            site=site,
            inviter=user,
            countable=True).count()
        max_invites = config_value('INVITES_SETTINGS', 'MAX_INVITES')
        if invites_sent > max_invites:
            raise self.model.OverQuota(user)
        # XXX: on linux system uuid1 returns less than 34 chars 
        code = "%x-%x-%x-%x%x-%x" % uuid1().fields
        code = code[:32]
        invite = self.model(
            site=site,
            code=code,
            inviter=user,
            recipient=recipient,
            recipient_name=recipient_name,
            recipient_surname=recipient_surname,
            text=text,
            used=False,
            countable=True)
        invite.save(from_manager=True)
        shop_config = Config.objects.get_current()
        send_store_mail(
            subject=_(u'You have been invited to join'
            u' by %(first_name)s %(last_name)s') % {
                'first_name': invite.inviter.first_name,
                'last_name': invite.inviter.last_name},
            context={
                'site_domain': site.domain,
                'recipient_name': invite.recipient_name,
                'inviter_name': invite.inviter.first_name,
                'inviter_surname': invite.inviter.last_name,
                'inviter_email': invite.inviter.email,
                'shop_description': shop_config.store_description,
                'registration_url': reverse(
                    'invites_register',
                    kwargs={ 'invite_code': invite.code }
                )
            },
            template='invites/mail/invite.txt',
            recipients_list=[invite.recipient],
            template_html='invites/mail/invite.html')
        return invite

    def reset_for_user(self, user, site=None):
        """Logically deletes invites sent by the passed user.

        This would practically mark these invites as invalid: not only they
        won't be counted towards the total maximum, but they won't be usable
        anymore.
        """
        if site is None:
            site = Site.objects.get_current()
        return self.all().filter(
            inviter=user,
            site=site,
            countable=True).update(countable=False)

    def get_for_user(self, user, used=False, countable=True, site=None):
        if site is None:
            site = Site.objects.get_current()
        return self.all().filter(
            inviter=user,
            site=site,
            used=used,
            countable=countable)
    
    def get_contact(self, user):
        try:
            contact = Contact.objects.get(user=user)
            return contact
        except Contact.DoesNotExist:
            return None
            
    def get_invited_by(self, inviter, used=True, site=None):
        if site is None:
            site = Site.objects.get_current()
        invites = self.all().filter(
            inviter=inviter,
            site=site,
            used=used)
        return [self.get_contact(invite.invited) for invite in invites \
                if self.get_contact(invite.invited) is not None]


class Invite(models.Model):
    """An invite to join the site
    """

    site = models.ForeignKey(Site, verbose_name=_(u'site'))
    code = models.SlugField(_(u'code'))
    inviter = models.ForeignKey(User, verbose_name=_(u'inviter'))
    invited = models.ForeignKey(User, verbose_name=_(u'invited'),
        related_name="invited_set", blank=True, null=True)
    recipient = models.EmailField(_(u'email address'))
    recipient_name = models.CharField(_(u'first name'), max_length=30)
    recipient_surname = models.CharField(_(u'last name'), max_length=30)
    text = models.TextField(_(u'personal note'), blank=True, null=True)
    used = models.BooleanField(_(u'used'), default=False)
    countable = models.BooleanField(_(u'has to be counted'), default=True)

    objects = InvitesManager()

    def save(self, *args, **kwargs):
        # BBB: these controls are here to prevent misuse of the API, and direct
        # instatiation and saving.
        #
        # Direct saving can be done after they have been created and saved the
        # first time, but no initial direct saving can be done.
        try:
            from_manager = kwargs.pop('from_manager')
        except KeyError:
            from_manager = False
        if self.id is None and not from_manager:
            raise RuntimeError(u"Invites cannot be directly instantiated and "
                               u"saved, but the manager's create function "
                               u"should be used instead")
        super(Invite, self).save(*args, **kwargs)
        if self.used == True:
            InviteDiscount.find_and_activate(self.site, self.inviter)

    class Meta:
        unique_together = (
            ('site', 'code'),
            ('site', 'inviter', 'recipient'))

    class OverQuota(Exception):
        """The user has exceeded the amount of invites it can send
        """


class InviteDiscount(models.Model):
    """A discount that activates after an invite target is met.

    If a user invites a certain number of users and they accept the invitation
    and subscribe, the discount is activated
    """

    site = models.ForeignKey(
        Site,
        verbose_name=_(u'site'))
    invites_target = models.IntegerField(
        _(u'invites target'),
        validators=[MinValueValidator(1)],
        help_text=_(u"the number of succesful invites that trigger the "
                    u"coupon creation"))
    amount = CurrencyField(
        _(u'absolute amount'),
        decimal_places=2,
        max_digits=8,
        blank=True,
        null=True,
        help_text=_(u"the absolute amount of the discount (e.g. 10€). "
                    u"You must set either this OR the percentage amount"))
    percentage = models.DecimalField(
        _(u'percentage amount'),
        decimal_places=2,
        max_digits=5,
        blank=True,
        null=True,
        help_text=_(u"the percentage amount of the discount, in absolute value"
                    u" (e.g. 30.0). "
                    u"You must set either this OR the absolute amount"))
    minOrder = CurrencyField(
        _(u'minimum order value'),
        decimal_places=2,
        max_digits=8,
        blank=True,
        null=True)
    shipping = models.CharField(
        _(u'shipping'),
        choices=DISCOUNT_SHIPPING_CHOICES,
        default='NONE',
        blank=True,
        null=True,
        max_length=10)
    daysValid = models.IntegerField(
        _(u'validity after activation'),
        validators=[MinValueValidator(1)],
        help_text=_(u"the coupon will be valid for the number of days "
                    u"specified after the mail has been sent to the discount "
                    u"recipient"))
    allValid = models.BooleanField(
        _(u'apply to all products'),
        default=False,
        help_text=_(u"Apply this discount to all discountable products? If "
                    u"this is false you must select products below in the "
                    u"'Valid Products' section."))
    valid_products = models.ManyToManyField(
        Product,
        verbose_name=_(u"valid on these products only"),
        blank=True,
        null=True)
    valid_categories = models.ManyToManyField(
        Category,
        verbose_name=_(u"valid on these categories only"),
        blank=True,
        null=True)

    def clean(self):
        if self.amount is None and self.percentage is None:
            raise ValidationError(_(u"You should specify either the absolute "
                                    u"amount or the percentage amount, but "
                                    u"you specified none of the two"))
        elif self.amount is not None and self.percentage is not None:
            raise ValidationError(_(u"You should specify either the absolute "
                                    u"amount or the percentage amount, but "
                                    u"you specified both"))

    def _activate(self, user):
        today = datetime.utcnow().date()
        code = "%x%x%x%x%x" % uuid1().fields[0:5]
        discount = Discount(
            site=self.site,
            description=_(u"Invite discount "
                u"for %(last_name)s %(first_name)s") % {
                    'last_name': user.last_name,
                    'first_name': user.first_name},
            code=code,
            active=True,
            amount=self.amount,
            percentage=self.percentage,
            automatic=False,
            allowedUses=1,
            minOrder=self.minOrder,
            startDate=today,
            endDate=today + timedelta(days=self.daysValid),
            shipping=self.shipping,
            allValid=self.allValid)
        discount.save()
        for product in self.valid_products.all():
            discount.valid_products.add(product)
        for category in self.valid_categories.all():
            discount.valid_categories.add(category)
        discount.save()
        discount_amount = None
        if self.amount is not None:
            discount_amount = moneyfmt(self.amount)
        else:
            discount_amount = "%s%%" % self.percentage
        send_store_mail(
            subject=_(u"A discount coupon for you"),
            context={
                'first_name': user.first_name,
                'invites_number': self.invites_target,
                'discount_amount': discount_amount,
                'coupon_code': discount.code,
                'end_date': discount.endDate},
            template='invites/mail/discount.txt',
            recipients_list=[user.email],
            template_html='invites/mail/discount.html')

        # create new InviterDiscount
        inviter_discount = InviterDiscount(
            user=user,
            coupon=discount,
            template=self)
        inviter_discount.save()
        return True

    def check_and_activate(self, user):
        succeeded_invites = Invite.objects.all().filter(
            inviter=user,
            used=True).count()
        if succeeded_invites >= self.invites_target:
            inviter_discount = InviterDiscount.objects.filter(
                user=user,
                template=self)
            if inviter_discount.count() == 0:
                return self._activate(user)
        return False

    @classmethod
    def find_and_activate(cls, site, user):
        discounts = cls.objects.all().filter(
            site=site).order_by('-invites_target')
        for discount in discounts:
            if discount.check_and_activate(user):
                break


class InviterDiscount(models.Model):
    """ A map that represents the User-InviteDiscount relationship """
    user = models.ForeignKey(User, verbose_name=_(u'inviter'))
    coupon = models.ForeignKey(Discount, verbose_name=_(u'discount'))
    template = models.ForeignKey(InviteDiscount,
        verbose_name=_(u'discount template'))

    class Meta:
        unique_together = ('user', 'template')
