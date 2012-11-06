# -*- coding: utf-8 -*-
import datetime
from django.core.validators import URLValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.loader import render_to_string
from registration.models import RegistrationProfile
from django.conf import settings

from product.models import Product
from satchmo_store.shop.models import Order
from satchmo_store.mail import send_store_mail
from satchmo_utils.thumbnail.field import ImageWithThumbnailField
from shipping.config import shipping_method_by_key

from primifrutti.zones.models import Shipment
from primifrutti.utils import HumanizeTimes


class HtmlRegistrationProfile(RegistrationProfile):

    class Meta:
        proxy = True

    def send_activation_email(self, site):
        """Send the activation mail"""
        ctx_dict = {'activation_key': self.activation_key,
                    'expiration_days': settings.ACCOUNT_ACTIVATION_DAYS,
                    'site': site}
        subject = render_to_string('registration/activation_email_subject.txt',
                                   ctx_dict)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        send_store_mail(
            subject=subject,
            context=ctx_dict,
            template='registration/activation_email.txt',
            recipients_list=[self.user.email],
            template_html='registration/activation_email.html')


class Offer(models.Model):
    """A promotion on the site
    """

    product = models.OneToOneField(
        Product,
        verbose_name=_(u"product"),
        help_text=_(u"the product being promoted"))
    title = models.CharField(
        _(u"headline"),
        help_text=_(u"a catching headline for your promotion"),
        max_length=255)
    main_description = models.TextField(
        _(u"description"),
        help_text=_(u"a more detailed description of the promotion"))
    ordering = models.IntegerField(
        _(u"ordering"),
        help_text=_(u"controls the order in which the promotions are shown. "
                    u"Those with a lower number will be shown first"),
        default=100)
    active = models.BooleanField(
        _(u"active"),
        help_text=_(u"if deselected, the offer doesn't appear on the site"),
        default=True)
    picture = ImageWithThumbnailField(
        upload_to="__DYNAMIC__",
        name_field="_filename",
        max_length=512,
        verbose_name=_(u"picture"))

    def _get_filename(self):
        if self.product.name:
            return '%s-%s' % (self.product.slug, self.pk)
        else:
            return 'offer-%s' % self.pk
    _filename = property(_get_filename) # pylint: disable=W1001

    def __unicode__(self):
        return _(u"%(title)s (for %(product)s)") % {
            'title': self.title,
            'product': unicode(self.product)}

    class Meta:
        ordering = ['ordering', 'title']
        verbose_name = _("offer")
        verbose_name_plural = _("offers")


class Banner(models.Model):
    """A banner on the splash page.
    """

    title = models.CharField(
        _(u"Banner"),
        max_length=255)
    url = models.CharField(
        _(u"link"),
        help_text=_(u"the address of the page the banner links to"),
        max_length=255,
        validators=[URLValidator()])
    active = models.BooleanField(
        _(u"active"),
        help_text=_(u"if deselected, the banner will not appear on the site"),
        default=True)
    picture = ImageWithThumbnailField(
        upload_to="__DYNAMIC__",
        name_field="_filename",
        max_length=512,
        verbose_name=_(u"picture"))

    def _get_filename(self):
        return 'bannerhome-%s' % self.pk
    _filename = property(_get_filename) # pylint: disable=W1001

    @property
    def link_url(self):
        return self.url

    def __unicode__(self):
        return _(u"Banner #%(id)s: %(title)s") % {
            'id': self.id,
            'title': self.title}

    class Meta:
        verbose_name = _("banner")
        verbose_name_plural = _("banners")


class ProductFeaturedSorting(models.Model):
    """A product that is featured within the home page.
    """

    product = models.ForeignKey(
        Product,
        verbose_name=_(u"product"),
        help_text=_(u"the product being featured"))
    ordering = models.IntegerField(
        _(u"ordering"),
        help_text=_(u"controls the order in which the products are shown "
                    u"within the homepage. Those with a lower number will "
                    u"be shown first"),
        default=100)

    def __unicode__(self):
        return _(u"%(product)s, featured (%(ordering)d)") % {
            'product': self.product,
            'ordering': self.ordering}

    class Meta:
        ordering = ['ordering']
        verbose_name = _("product featured sorting")
        verbose_name_plural = _("products featured sorting")


# Patch Product
def get_main_units(self):
    product = self
    units = [p for p in product.productattribute_set.all() \
                                        if p.option.name == 'unita-di-misura']
    if units:
        units = units[0].value
    else:
        units = u'Kg' # default value
    return units

Product.add_to_class("get_main_units", get_main_units)


# Patch Order
def shipping_extimated_date(self):
    order = self
    method = shipping_method_by_key(order.shipping_model)
    if method.valid():
        expected_delivery = method.expectedDelivery(order.contact)

    try:
        shipment = Shipment.objects.get(order=order)
        humanize_times = HumanizeTimes()
        start = shipment.mission.starts
        end = shipment.mission.ends
        start_str = start.strftime("%H:%M")
        end_str = end.strftime("%H:%M")
        now = datetime.datetime.utcnow().date()
        if now < shipment.date:
            expected_delivery = humanize_times.humanizeTimeDiffLeft(
                                                            shipment.date)
        else:
            expected_delivery = humanize_times.humanizeTimeDiffAgo(
                                                            shipment.date)

        return u"%(date)s, %(start)s - %(end)s" % {
            'date': expected_delivery,
            'start': start_str,
            'end': end_str}

    except Shipment.DoesNotExist:
        pass

    return expected_delivery


Order.add_to_class("shipping_extimated_date", shipping_extimated_date)

import signals # pylint: disable=W0611
