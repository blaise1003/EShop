"""
URLConf for Satchmo Contacts.
"""

from django.conf.urls.defaults import patterns
from signals_ahoy.signals import collect_urls
from satchmo_store import contact
from satchmo_store.shop.satchmo_settings import get_satchmo_setting

ssl = get_satchmo_setting('SSL', default_value=False)

urlpatterns = patterns('satchmo_store.contact.views',
    (r'^$', 'view', {}, 'satchmo_account_info'),
    (r'^update/$', 'update', {}, 'satchmo_profile_update'),
    (r'^address/create/$', 'address_create_edit',{},'satchmo_address_create'),
    (r'^address/edit/(?P<id>\d+)/$','address_create_edit',{},'satchmo_address_edit'),
    (r'^address/delete/(?P<id>\d+)/$','address_delete',{},'satchmo_address_delete'),
    (r'^ajax_state/$', 'ajax_get_state', {'SSL': ssl}, 'satchmo_contact_ajax_state'),
)

collect_urls.send(sender=contact, patterns=urlpatterns)
