# -*- coding: utf-8 -*-
from livesettings import config_register, ConfigurationGroup, IntegerValue
from django.utils.translation import ugettext_lazy as _


# Shop configs
INVITES_SETTINGS = ConfigurationGroup(
    'INVITES_SETTINGS',
    _(u'Invites settings'),
    ordering=1)


config_register(
    IntegerValue(
        INVITES_SETTINGS,
        'MAX_INVITES',
        description=_(u'Maximum invites'),
        help_text=_(u"The maximum number of invites a user can send"),
        default=10))
