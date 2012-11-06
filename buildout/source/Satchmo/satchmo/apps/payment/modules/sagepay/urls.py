from django.conf.urls.defaults import patterns
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
     (r'^$', 'payment.modules.sagepay.views.pay_ship_info',
        {'SSL':ssl}, 'SAGEPAY_satchmo_checkout-step2'),

     (r'^confirm/$', 'payment.modules.sagepay.views.confirm_info',
        {'SSL':ssl}, 'SAGEPAY_satchmo_checkout-step3'),

    (r'^secure3d/$', 'payment.modules.sagepay.views.confirm_secure3d',
       {'SSL':ssl}, 'SAGEPAY_satchmo_checkout-secure3d'),

     (r'^success/$', 'payment.views.checkout.success',
        {'SSL':ssl}, 'SAGEPAY_satchmo_checkout-success'),
)
