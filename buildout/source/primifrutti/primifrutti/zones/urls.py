from django.conf.urls.defaults import url, patterns
from django.contrib.auth.decorators import user_passes_test

from .views import deliveries, stale_shipments, confirm_shipment


is_staff = user_passes_test(lambda u: u.is_authenticated() and u.is_staff)

urlpatterns = patterns(
    'primifrutti.zones.views',
    url(r'^admin/zones/stale_shipments/$',
        is_staff(stale_shipments),
        {},
        'satchmo_stale_shipments'),
    url(r'^admin/zones/deliveries/$',
        is_staff(deliveries),
        {},
        'satchmo_deliveries'),
    url(r'admin/zones/confirm_shipment/(?P<id>[-\w]+)/$',
        is_staff(confirm_shipment),
        {},
        'satchmo_confirm_shipment'))
