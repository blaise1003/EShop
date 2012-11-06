from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _


class AdminLinksExtender(object):

    @classmethod
    def get_admin_links(self):
        return [
            {'name': _(u'Export Categories CSV'),
            'url': reverse('satchmo_export_categories_csv')},
            {'name': _(u'Export Products CSV'),
            'url': reverse('satchmo_export_products_csv')},
        ]