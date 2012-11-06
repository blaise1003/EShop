from django import template
from livesettings import config_value

from ..models import Invite

register = template.Library()


@register.inclusion_tag('tags/invite_box.html', takes_context=True)
def invite_box(context, user=None):
    max_invites = int(config_value('INVITES_SETTINGS', 'MAX_INVITES'))
    invites = Invite.objects.get_for_user(user, countable=True).count()
    invites_available = user and user.is_authenticated \
                                and (invites < max_invites)
    return {'invites_available': invites_available}
