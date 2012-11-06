from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import (config_register, ConfigurationGroup,
                          DecimalValue, StringValue)


BANNERS_INFO = ConfigurationGroup(
    'BANNERS_INFO',
    _(u'Banners info'),
    ordering=0)

config_register(
    DecimalValue(
        BANNERS_INFO,
        'NUM_MAX',
        description=_(u'Offers in splash page'),
        help_text=_(u"sets the maximum number of offers to be shown in the "
                    u"splash page"),
        default=Decimal('3')))

# SOCIALS_INFO configs
SOCIALS_INFO = ConfigurationGroup(
    'SOCIALS_INFO',
    _('Socials urls info'),
    ordering=0
)

# facebook
config_register(
    StringValue(
        SOCIALS_INFO,
        'FACEBOOK_URL',
        description=_(u'Facebook url'),
        help_text=_(u"Insert personal facebook url"),
        default="",
    )
)

# twitter
config_register(
    StringValue(
        SOCIALS_INFO,
        'TWITTER_URL',
        description=_('Twitter url'),
        help_text=_(u"Insert personal twitter url"),
        default="",
    )
)

# linkedin
config_register(
    StringValue(
        SOCIALS_INFO,
        'LINKEDIN_URL',
        description=_('Linkedin url'),
        help_text=_(u"Insert Linkedin url"),
        default="",
    )
)

# username skype
config_register(
    StringValue(
        SOCIALS_INFO,
        'SKYPE_CONTACT',
        description=_('username skype'),
        help_text=_(u"Insert personal skype username"),
        default="",
    )
)
