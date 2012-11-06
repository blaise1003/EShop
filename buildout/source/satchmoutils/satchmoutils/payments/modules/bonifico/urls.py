from django.conf.urls.defaults import patterns
from livesettings import config_get_group
from satchmo_store.shop.satchmo_settings import get_satchmo_setting
ssl = get_satchmo_setting('SSL', default_value=False)

config = config_get_group('PAYMENT_BONIFICO')

urlpatterns = patterns('',
    (r'^$', 'satchmoutils.payments.modules.bonifico.views.pay_ship_info', 
        {'SSL': ssl}, 'BONIFICO_satchmo_checkout-step2'),
    (r'^confirm/$', 'satchmoutils.payments.modules.bonifico.views.confirm_info', 
        {'SSL':ssl}, 'BONIFICO_satchmo_checkout-step3'),
    (r'^success/$', 'satchmoutils.payments.modules.views.multisuccess_view', 
        {'SSL': ssl}, 'BONIFICO_satchmo_checkout-success'),    
)
