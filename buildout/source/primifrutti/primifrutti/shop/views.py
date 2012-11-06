# -*- coding: utf-8 -*-
import json
import time
import csv
from django.contrib.sites.models import Site
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, TemplateView
from django.views.decorators.cache import never_cache
from django.core import urlresolvers
from django.http import HttpResponse, HttpResponseRedirect

from ajax_select import get_lookup
from signals_ahoy.signals import application_search
from product.utils import find_best_auto_discount
from product.models import Product, Category
from product.signals import index_prerender
from satchmoutils.utils import ShopUtils

from payment.views.contact import contact_info_view
from .models import Offer, Banner


category_headers = [
    'id',
    'Active (0/1)',
    'Name*',
    'Parent Category',
    'Description',
    'Meta-title',
    'Meta-keywords',
    'Meta-description',
    'URL rewritten',
    'Image URL']

product_headers = [
    'id',
    'Active (0/1)',
    'Name*',
    'Categories (x,y,z,...)',
    'Price tax excl. Or Price tax excl',
    'Tax rules id',
    'Wholesale price',
    'On sale (0/1)',
    'Discount amount',
    'Discount percent',
    'Discount from (yyy-mm-dd)',
    'Discount to (yyy-mm-dd)',
    'Reference #',
    'Supplier reference #',
    'Supplier',
    'Manufacturer',
    'EAN13',
    'UPC',
    'Ecotax',
    'Weight',
    'Quantity',
    'Short description',
    'Description',
    'Tags (x,y,z,...)',
    'Meta-title',
    'Meta-keywords',
    'Meta-description',
    'URL rewritten',
    'Text when in-stock',
    'Text if back-order allowed',
    'Image URLs (x,y,z,...)',
    'Feature:Height',
    'Feature:battery life',
    'Only available online',
]

if "primifrutti.zones" in settings.INSTALLED_APPS:
    HAS_ZONES_APP = True
    from primifrutti.zones.models import Zone
else:
    HAS_ZONES_APP = False


class CategoriesSitemap(object):

    @classmethod
    def items(self):
        return Category.objects.filter(is_active=True)


class ProductsSitemap(object):

    @classmethod
    def items(self):
        return Product.objects.filter(active=True)


class Sitemap(TemplateView):
    """HTML Sitemap.
    """

    template_name = "shop/sitemap.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Sitemap, self).get_context_data(**kwargs)
        # Add some values to context
        context['categories'] = CategoriesSitemap.items()
        context['products'] = ProductsSitemap.items()
        return context


pf_sitemap = Sitemap.as_view()


class SplashPage(ListView):
    """The initial splash page.
    """

    context_object_name = "offer_list"
    template_name = "shop/splash_page.html"

    def get_queryset(self):
        return Offer.objects.order_by('ordering')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SplashPage, self).get_context_data(**kwargs)
        # Add some values to context
        shop_utils = ShopUtils()
        context.update(shop_utils.get_shop_config())
        context['home_url'] = urlresolvers.reverse('satchmo_home')
        return context


splash = SplashPage.as_view()


class SearchView(ListView):
    context_object_name = "list_products"
    template_name = "shop/search.html"
    paginate_by = 10

    def get_queryset(self):

        if self.request.method == "GET":
            data = self.request.GET
        else:
            data = self.request.POST

        self.keywords = data.get('keywords', '').split(' ')
        self.category = data.get('category', None)

        self.keywords = filter(None, self.keywords)

        item_results = {}
        self.list_products = []
        self.categories = []
        # this signal will usually call listeners.default
        # product_search_listener
        application_search.send(Product, request=self.request,
            category=self.category, keywords=self.keywords,
            results=item_results)

        if item_results:
            self.list_products = item_results['products']
        #    self.categories = item_results['categories']

        return self.list_products or []

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(SearchView, self).get_context_data(**kwargs)
        # Add some values to context
        count = 0
        if self.list_products:
            count = len(self.list_products)
        context['results_count'] = count
        return context

search_view = SearchView.as_view()


class Home(TemplateView):
    """The home page (shown after the splash).
    """

    template_name = "shop/home.html"

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Home, self).get_context_data(**kwargs)
        # Add some values to context
        context['banner_list'] = Banner.objects.filter(active=True)
        featured = Product.objects.filter(active=True,
            featured=True).order_by('productfeaturedsorting__ordering')
        context['featured_first'] = None
        context['featured_list'] = []
        if featured:
            context['featured_first'] = featured[0]
            context['featured_list'] = featured[1:]
        context['user'] = self.request.user
        return context


home = Home.as_view()


class OffersPage(ListView):
    """The offers page.
    Shows the list of products promoted as offers.
    """
    context_object_name = "offer_list"
    template_name = "shop/offers_page.html"
    paginate_by = 9

    def get_queryset(self):
        return Offer.objects.filter(active=True).order_by('ordering')

    def get_context_data(self, **kwargs):
        context = super(OffersPage, self).get_context_data(**kwargs)
        return context


offers = OffersPage.as_view()


class CategoryIndexView(ListView):
    template_name = "product/category_index.html"
    context_object_name = "categorylist"
    paginate_by = 9

    def get_queryset(self):
        self.categorylist = Category.objects.root_categories()
        return self.categorylist

    def get_context_data(self, **kwargs):
        context = super(CategoryIndexView, self).get_context_data(**kwargs)
        return context

category_index = CategoryIndexView.as_view()


class CategoryView(ListView):
    template_name = "product/category.html"
    context_object_name = "products"
    paginate_by = 9
    model = Category

    def get_queryset(self):
        self.category = get_object_or_404(
                Category,
                slug__iexact=self.kwargs['slug']
        )
        self.products = list(self.category.active_products())
        return self.products

    def get_context_data(self, **kwargs):
        context = super(CategoryView, self).get_context_data(**kwargs)
        context['category'] = self.category
        context['child_categories'] = self.category.get_all_children()
        context['sale'] = find_best_auto_discount(self.products)
        context['parent_slugs'] = self.kwargs['parent_slugs']

        index_prerender.send(Product, request=self.request, context=context,
                             category=self.category, object_list=self.products)
        return context

category_view = CategoryView.as_view()


def ajax_lookup(request, channel):
    """The view used by the autocomplete widget to find products.
    """
    # it should come in as GET unless global $.ajaxSetup({type:"POST"}) has
    # been set in which case we'll support POST
    if request.method == "GET":
        query = request.GET['q']
    else:
        query = request.POST['q']
    lookup_channel = get_lookup(channel)
    if query:
        instances = lookup_channel.get_query(query, request)
    else:
        instances = []
    results = []
    for item in instances:
        itemf = lookup_channel.format_item(item)
        itemf = itemf.replace("\n", "").replace("|", "&brvbar;")
        resultf = lookup_channel.format_result(item)
        resultf = resultf.replace("\n", "").replace("|", "&brvbar;")
        results.append("|".join((unicode(item.pk), itemf, resultf)))
    return HttpResponse(
        json.dumps(results),
        mimetype='application/json')


class CheckoutNoZones(TemplateView):
    """
    Error page for checkout process if no shipping
    zones are configured by shop admin """

    template_name = "shop/nozones.html"


checkout_nozones = CheckoutNoZones.as_view()


def checkout_chek_zones(request):
    if HAS_ZONES_APP:
        active_zones = Zone.objects.filter(active=True)
        if not active_zones.count():
            return HttpResponseRedirect(urlresolvers.reverse(
                                    'satchmo_checkout-nozones'))

    return contact_info_view(request)


# Export in CSV
def force_encode(value, encoding='utf-8'):
    if not value:
        return ''
    return value.encode(encoding)


def get_discount(product):
    best_discount = find_best_auto_discount([product,])
    return best_discount


def export_categories_csv(request):
    """Export all categories in CSV"""
    mimetype = "text/csv"
        
    response = HttpResponse(mimetype=mimetype)
    ch = 'attachment; filename="categories-%s.csv"' % (time.strftime('%Y%m%d-%H%M'))
    response['Content-Disposition'] = ch
    writer = csv.writer(response, delimiter=';', quotechar='"',
                                                    quoting=csv.QUOTE_MINIMAL)
    writer.writerow(category_headers)

    site = Site.objects.get_current()
    domain = "http://%s" % site.domain
    categories = Category.objects.all().order_by('id')
    for category in categories:
        row = [
            u"%s" % category.id,
            category.is_active and u'1' or u'0',
            force_encode(category.translated_name()),
            category.parent and category.parent.slug or u'',
            force_encode(category.translated_description()),
            category.slug,
            u'',
            force_encode(category.meta),
            u"%s%s" % (domain, category.get_absolute_url()),
            ' :: '.join([u"%s%s" % (domain, image.picture.url) for image in \
                                            category.images.all()]),
        ]
        writer.writerow(row)

    return response


def export_products_csv(request):
    """Export all categories in CSV"""
    mimetype = "text/csv"
        
    response = HttpResponse(mimetype=mimetype)
    ch = 'attachment; filename="products-%s.csv"' % (time.strftime('%Y%m%d-%H%M'))
    response['Content-Disposition'] = ch
    writer = csv.writer(response, delimiter=';', quotechar='"',
                                                quoting=csv.QUOTE_MINIMAL)
    writer.writerow(product_headers)

    site = Site.objects.get_current()
    domain = "http://%s" % site.domain
    products = Product.objects.all().order_by('id')
    for product in products:
        discount = get_discount(product)
        discount_amount = discount and discount.amount or u''
        discount_percentage = discount and discount.percentage or u''
        discount_from = discount and discount.startDate.strftime("%Y-%m-%d") or u''
        discount_to = discount and discount.endDate.strftime("%Y-%m-%d") or u''
        row = [
            u"%s" % product.id,
            product.active and u'1' or u'0',
            force_encode(product.translated_name()),
            ' :: '.join([c.slug for c in product.category.all()]),
            u"%0.2f" % product.unit_price,
            product.taxClass and product.taxClass.id or u'',
            u"%0.2f" % product.unit_price,
            product.in_stock() and u'1' or u'0',
            discount_amount,
            discount_percentage,
            discount_from,
            discount_to,
            u'',
            u'',
            u'',
            u'',
            u'',
            u'',
            u'',
            product.weight or u'',
            product.items_in_stock,
            force_encode(product.meta),
            force_encode(product.translated_description()),
            u'',
            product.slug,
            u'',
            force_encode(product.meta),
            u"%s%s" % (domain, product.get_absolute_url()),
            u'',
            u'',
            ' :: '.join([u"%s%s" % (domain, image.picture.url) for image in \
                                            product.productimage_set.all()]),
            product.height or u'',
            u'',
            u'0'
        ]
        writer.writerow(row)

    return response


# Never cache csv ezport views
export_categories_csv = never_cache(export_categories_csv)
export_products_csv = never_cache(export_products_csv)
