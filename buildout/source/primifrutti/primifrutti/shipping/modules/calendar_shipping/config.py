from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('primifrutti.shipping.modules.calendar_shipping',
    _(u'Calendar shipping')))

SHIPPING_GROUP = config_get_group('SHIPPING')


config_register_list(

    BooleanValue(SHIPPING_GROUP,
        'ACTIVE',
        description=_(u"Make shipping for zones active"),
        help_text=_(u"False if you don't want to ship for zone and calendar"),
        default=True),

    DecimalValue(SHIPPING_GROUP,
        'SHIPPING_RATE',
        description=_(u"Shipping standard cost"),
        requires=SHIP_MODULES,
        requiresvalue='primifrutti.shipping.modules.calendar_shipping',
        default="0.0"),)
