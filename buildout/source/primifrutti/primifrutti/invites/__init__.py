from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class AdminLinksExtender(object):

    @classmethod
    def get_admin_links(self):
        return [
            {'name': _(u'Invites report'),
            'url': reverse('satchmo_invites_report')},
            {'name': _(u'Invites relationships'),
            'url': reverse('satchmo_invites_relationships')},
        ]
