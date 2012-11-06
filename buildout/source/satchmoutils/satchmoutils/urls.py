from django.conf.urls.defaults import patterns, url, include
from satchmo_store.shop import get_satchmo_setting

pages = r'^' + get_satchmo_setting('PAGE_SLUG') + '/'

urlpatterns = patterns('',
    url(r'^cart/empty/$',
        'satchmoutils.views.cart_empty', {}, 'satchmo_cart_empty'),
    url(r"^test_confirm_ipn/",
        'satchmoutils.test_views.test_confirm_ipn', {}, 'test_confirm_ipn'),
    url(pages + '(?P<slug>[-\w]+)/$',
        'satchmoutils.views.get_static_page', {}, 'page_url'),
    url(r'^contact/$',
        'satchmoutils.views.contact_form', {}, 'satchmo_contact'),
    url(r"^captcha/", include('captcha.urls')))
