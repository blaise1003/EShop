from decimal import Decimal, InvalidOperation
from django.contrib.sites.models import Site
from django.db.models import Q
from livesettings import config_value
from product.models import Product, Category, Discount
import logging

log = logging.getLogger('search listener')

def default_product_search_listener(sender, request=None, category=None, keywords=[], results={}, **kwargs):
    """Performs the base satchmo search.  This is easily overridden by unregistering the listener and creating your own.
    However, it usually won't have to be overridden, since it just adds data to the results dict.  If you are simply
    adding more results, then leave this listener registered and add more objects in your search listener.
    """
    log.debug('default product search listener')
    site = Site.objects.get_current()
    productkwargs = {}

    show_pv = config_value('PRODUCT','SEARCH_SHOW_PRODUCTVARIATIONS', False)

    if keywords:
        products = Product.objects.active_by_site(variations=show_pv, site=site, **productkwargs)
        pl = list(products)
        log.debug('initial: %s\n%s', pl, productkwargs)

        #automatically assumes active categories only
        categories = Category.objects.by_site(site=site)
    else:
        products = None
        categories = None

    if category:
        categories = Category.objects.active(site=site, slug=category)
        if categories:
            categories = categories[0].get_active_children(include_self=True)
        products.filter(category__in = categories)

    for keyword in keywords:
        if not category:
            categories = categories.filter(
                Q(name__icontains=keyword) |
                Q(meta__icontains=keyword) |
                Q(description__icontains=keyword))

        products = products.filter(
            Q(name__icontains=keyword)
            | Q(short_description__icontains=keyword)
            | Q(description__icontains=keyword)
            | Q(meta__icontains=keyword)
            | Q(sku__iexact=keyword) )

    results.update({
        'categories': categories,
        'products': products
        })

def priceband_search_listener(sender, request=None, category=None, keywords=[], results={}, **kwargs):
    """Filter search results by price bands.

    If a "priceband" parameter is available, it will be parsed as follows:
        lowval-highval
        if there is no "-", then it will be parsed as lowval or higher
    """
    log.debug('priceband search listener')
    if request.method=="GET":
        data = request.GET
    else:
        data = request.POST

    priceband = data.get('priceband', None)

    if not priceband:
        return

    bands = priceband.split('-')
    try:
        if len(bands) > 1:
            low = int(bands[0])
            high = int(bands[1])
        else:
            low = bands[0]
            high = Decimal('1000000000.00')
    except (TypeError, InvalidOperation):
        log.warn("Couldn't parse priceband=%s", priceband)
        return

    priced = []
    products = results['products']
    log.debug('priceband pre-filter length=%i', len(products))
    for p in products:
        price = p.unit_price
        if price>low and price<=high:
            priced.append(p)
    log.debug('priceband post-filter length=%i', len(priced))

    categories = results['categories']
    categories = categories.filter(product__in = priced)
    results['products'] = priced
    results['categories'] = categories

def discount_used_listener(sender, order=None, **kwargs):
    """If an order has a discount, increment numUses on it.

    satchmo_store.shop.signals.order_success listener set up in shop.listeners.
    """
    if order.discount_code:
        try:
            discount = Discount.objects.by_code(order.discount_code)
            if discount.numUses:
                discount.numUses += 1
            else:
                discount.numUses = 1
            discount.save()
        except Discount.DoesNotExist:
            pass
