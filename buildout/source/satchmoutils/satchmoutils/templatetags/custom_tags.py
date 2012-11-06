from django import template
from django.conf import settings

from ..formextender import import_path
from ..models import Page

register = template.Library()


@register.inclusion_tag('tags/admin_extra_links.html', takes_context=True)
def admin_extra_links(context):
    """Reads the setting ``SATCHMO_SETTINGS['EXTRA_LINKS']``, which is a
    list of apps in the form ``dotted.name.of.module:Class``, and loads
    them
    """
    satchmo_settings = getattr(settings, 'SATCHMO_SETTINGS', {})
    admin_extra_links = []
    extenders = [
        import_path(p) for p in satchmo_settings.get('EXTRA_LINKS', [])]
    for extender in extenders:
        admin_extra_links.extend(
            extender.get_admin_links())
    return {'admin_extra_links': admin_extra_links}


@register.inclusion_tag('tags/pages_links.html', takes_context=True)
def pages_links(context):
    """Box for Pages list
    Default limit to 10 pages"""
    default_pages = [
        'l-azienda',
        'condizioni-spedizione',
        'tipologie-pagamento',
        'buono-regalo',
    ]
    pages = Page.objects.filter(active=True).order_by('ordering', 'title')
    pages = [p for p in pages if p.slug not in default_pages][:10]
    return {'pages': pages}
