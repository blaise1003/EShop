from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class AdminLinksExtender(object):

    @classmethod
    def get_admin_links(self):
        return [
            {'name': _(u'Stale shipments'),
            'url': reverse('satchmo_stale_shipments')}
        ]
