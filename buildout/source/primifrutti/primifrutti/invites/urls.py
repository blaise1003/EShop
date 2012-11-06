from django.conf.urls.defaults import patterns, url, include
from django.contrib.auth.decorators import user_passes_test

from .views import invites_relationships, invites_report, invites_reset


is_staff = user_passes_test(lambda u: u.is_authenticated() and u.is_staff)


# Invites Frontend Urls
frontend = patterns(
    'primifrutti.invites.views',
    url(r'^register/(?P<invite_code>[a-f0-9\-]{32})/$',
     'register_from_invite',
     {},
     'invites_register'),
    url(r'confirm/(?P<invite_code>[a-f0-9\-]{32})/$',
     'confirm',
     {},
     'invites_confirm'),
    url(r'invite_friends/$',
     'invite',
     {},
     'invites_invite'))


# Invites Admin Urls
admin = patterns(
    'primifrutti.invites.views',
    url(r'^zones/invites_relationships/$',
        is_staff(invites_relationships),
        {},
        'satchmo_invites_relationships'),
    url(r'^zones/invites_report/$',
        is_staff(invites_report),
        {},
        'satchmo_invites_report'),
    url(r'zones/invites_reset/(?P<user_id>[-\w]+)/$',
        is_staff(invites_reset),
        {},
        'satchmo_invites_reset'))

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin)),
    (r'^invites/', include(frontend))
)
