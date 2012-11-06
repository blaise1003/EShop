from django.conf import settings
from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import logging
import re

try:
    import django.contrib.staticfiles
    view = 'django.contrib.staticfiles.views.serve'
except ImportError:
    view = 'django.views.static.serve'   # for Django 1.2

log = logging.getLogger('satchmo_store.urls')

# discover all admin modules - if you override this for your
# own base URLs, you'll need to autodiscover there.
admin.autodiscover()

urlpatterns = getattr(settings, 'URLS', [])

adminpatterns = patterns('',
     (r'^admin/', include(admin.site.urls)),
)

if urlpatterns:
    urlpatterns += adminpatterns
else:
    urlpatterns = adminpatterns

#The following is used to serve up local media files like product images
prefix = settings.MEDIA_URL
if getattr(settings, 'LOCAL_DEV', False) and prefix and not '://' in prefix:
    log.debug("Adding local serving of media files '%s' at: %s", prefix, \
            settings.MEDIA_ROOT)
    urlpatterns += patterns('',
        # usually r'^media/(?P<path>.*)$'
        url(r'^%s(?P<path>.*)$' % re.escape(prefix.lstrip('/')), view,
        {'document_root':  settings.MEDIA_ROOT}),
    )

# Removed prefix '^site_media/' because it is very old, unused, duplicated,
# undocumented and a replacement is easy.
