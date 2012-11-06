from django.conf.urls.defaults import patterns
from livesettings import config_get_group
from satchmo_store.shop.satchmo_settings import get_satchmo_setting
ssl = get_satchmo_setting('SSL', default_value=False)

config = config_get_group('PAYMENT_CREDITCARD')
ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('',
    (r'^$', 'satchmoutils.payments.modules.creditcard.views.pay_ship_info', 
        {'SSL': ssl}, 'CREDITCARD_satchmo_checkout-step2'),
    (r'^confirm/$', 'satchmoutils.payments.modules.creditcard.views.confirm_info', 
        {'SSL': ssl}, 'CREDITCARD_satchmo_checkout-step3'),
    (r'^success/$', 'satchmoutils.payments.modules.creditcard.views.success', 
        {'SSL': ssl}, 'CREDITCARD_satchmo_checkout-success'),
    (r'^error/$', 'satchmoutils.payments.modules.creditcard.views.error', 
        {'SSL': ssl}, 'CREDITCARD_satchmo_checkout-error'),
    (r'^confirmorder/$', 'payment.views.confirm.confirm_free_order', 
        {'SSL' : ssl, 'key' : 'CREDITCARD'}, 'CREDITCARD_satchmo_checkout_free-confirm')
)