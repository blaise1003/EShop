from django.conf import settings
from django.conf.urls.defaults import *
from django.conf.urls.static import static
from satchmo_store.urls import urlpatterns as storepatterns
from l10n.urls import urlpatterns as l10npatterns

from satchmoutils.urls import urlpatterns as satchmoutilspatterns
from primifrutti.zones.urls import urlpatterns as zonespatterns
from primifrutti.shop.urls import urlpatterns as shoppatterns
from primifrutti.invites.urls import urlpatterns as invitespatterns

urlpatterns = shoppatterns + invitespatterns + satchmoutilspatterns + \
    storepatterns + zonespatterns + l10npatterns


if getattr(settings, 'LOCAL_DEV', False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
