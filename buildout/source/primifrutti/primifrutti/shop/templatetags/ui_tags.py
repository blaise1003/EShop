# pylint: disable=W0613
from decimal import Decimal
from livesettings import config_value
from django import template
from django.utils.translation import ugettext as _

from satchmoutils.models import Page

from ..models import Offer, Banner
from ..utils import CategoriesPortlet


register = template.Library()


@register.inclusion_tag('tags/page_link.html', takes_context=True)
def page_link(context, slug):
    try:
        page = Page.objects.get(slug=slug, active=True)
    except Page.DoesNotExist:
        page = None
    return {'page': page}


@register.inclusion_tag('tags/offer_box.html', takes_context=True)
def offer_box(context):
    offer = Offer.objects.order_by('ordering')
    if offer:
        offer = offer[0]
    else:
        offer = None
    return {'offer': offer}


@register.inclusion_tag('tags/gift_box.html', takes_context=True)
def gift_box(context):
    gift_category = config_value('GIFT_INFO', 'GIFT_CATEGORY')
    if gift_category:
        gifts = gift_category.active_products(include_children=True)
    else:
        gifts = []

    if gifts:
        gift = gifts[0]
    else:
        gift = None
    return {'gift': gift}


@register.inclusion_tag('tags/banners.html', takes_context=True)
def banners(context):
    banner_list = Banner.objects.filter(active=True)
    return {'banner_list': banner_list}


@register.inclusion_tag('tags/prices_table.html', takes_context=True)
def prices_table(context, product):
    units = [p for p in product.productattribute_set.all() \
                                        if p.option.name == 'unita-di-misura']
    if units:
        units = units[0]
    else:
        units = _(u"pz")
    prices = [p for p in product.price_set.all() if p.quantity > Decimal('1')]
    return {'prices': prices, 'product': product, 'units': units}


@register.inclusion_tag('tags/index_categories.html', takes_context=True)
def index_categories(context):
    """Returns categories portlet html
    """
    categories_utils = CategoriesPortlet(context)
    return categories_utils.render()


# XXX: I'm not sure this filter is necessary
@register.filter
def make_integer(value=0):
    if isinstance(value, Decimal) or isinstance(value, float):
        return int(value)
    return value

@register.filter
def product_tax(product):
    return "%d%%" % int(product.taxClass.taxrate_set.all()[0].percentage * 100)
