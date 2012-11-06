from django.conf.urls.defaults import patterns, url, include
from satchmo_store.shop import get_satchmo_setting


pages = r'^' + get_satchmo_setting('PAGE_SLUG') + '/'
categories = r'^' + get_satchmo_setting('CATEGORY_SLUG') + '/'


urlpatterns = patterns(
    '',
    url(
        r'^ajax_select/ajax_lookup/(?P<channel>[-\w]+)$',
        'primifrutti.shop.views.ajax_lookup',
        name='ajax_lookup'),
    url(r'^$',
        'primifrutti.shop.views.splash',
        name='satchmo_shop_splash'),
    url(r'^home/$',
        'primifrutti.shop.views.home',
        name='satchmo_home'),
    url(r'^checkout/$',
        'primifrutti.shop.views.checkout_chek_zones',
        name='satchmo_checkout-step1'),
    url(r'^checkout_nozones/$',
        'primifrutti.shop.views.checkout_nozones',
        name='satchmo_checkout-nozones'),
    url(r'^search/$', 'primifrutti.shop.views.search_view', {},
        'satchmo_search'),
    url(pages + 'offerte/$',
        'primifrutti.shop.views.offers',
        name='satchmo_offers'),
    url(categories + '$',
        'primifrutti.shop.views.category_index',
        name='satchmo_category_index'),
    url(categories + '(?P<parent_slugs>([-\w]+/)*)?(?P<slug>[-\w]+)/$',
        'primifrutti.shop.views.category_view', name='satchmo_category'),
    url(r'^sitemap$', 'primifrutti.shop.views.pf_sitemap', name='pf_sitemap'),
    url(r'^admin/export_categories_csv$', 'primifrutti.shop.views.export_categories_csv', name='satchmo_export_categories_csv'),
    url(r'^admin/export_products_csv$', 'primifrutti.shop.views.export_products_csv', name='satchmo_export_products_csv'),
    url(r'^accounts/', include('primifrutti.shop.backends.urls')),)
