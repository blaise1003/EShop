from decimal import Decimal
from django.utils.translation import ugettext_lazy as _
from livesettings import *

SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('shipping.modules.ups', 'UPS'))

SHIPPING_GROUP = ConfigurationGroup('shipping.modules.ups',
    _('UPS Shipping Settings'),
    requires = SHIP_MODULES,
    ordering = 101)

config_register_list(

    StringValue(SHIPPING_GROUP,
        'XML_KEY',
        description=_("UPS XML Access Key"),
        help_text=_("XML Access Key Provided by UPS"),
        default=u""),

    StringValue(SHIPPING_GROUP,
        'USER_ID',
        description=_("UPS User ID"),
        help_text=_("User ID provided by UPS site."),
        default=u""),

    StringValue(SHIPPING_GROUP,
        'ACCOUNT',
        description=_("UPS Account Number"),
        help_text=_("UPS Account Number."),
        default=u""),

    StringValue(SHIPPING_GROUP,
        'USER_PASSWORD',
        description=_("UPS User Password"),
        help_text=_("User password provided by UPS site."),
        default=u""),

    MultipleStringValue(SHIPPING_GROUP,
        'UPS_SHIPPING_CHOICES',
        description=_("UPS Shipping Choices Available to customers. These are valid domestic codes only."),
        choices = (
            (('01', 'Next Day Air')),
            (('02', 'Second Day Air')),
            (('03', 'Ground')),
            (('12', '3 Day Select')),
            (('13', 'Next Day Air Saver')),
            (('14', 'Next Day Air Early AM')),
            (('59', '2nd Day Air AM')),
        ),
        default = ('03',)),

     DecimalValue(SHIPPING_GROUP,
        'HANDLING_FEE',
        description=_("Handling Fee"),
        help_text=_("The cost of packaging and getting the package off"),
        default=Decimal('0.00')),

    StringValue(SHIPPING_GROUP,
        'SHIPPING_CONTAINER',
        description=_("Type of container used to ship product."),
        choices = (
            (('00', 'Unknown')),
            (('01', 'UPS LETTER')),
            (('02', 'PACKAGE / CUSTOMER SUPPLIED')),
        ),
        default = u"00"),

    BooleanValue(SHIPPING_GROUP,
        'SINGLE_BOX',
        description=_("Single Box?"),
        help_text=_("Use just one box and ship by weight?  If no then every item will be sent in its own box."),
        default=True),

    BooleanValue(SHIPPING_GROUP,
        'TIME_IN_TRANSIT',
        description=_("Time in Transit?"),
        help_text=_("Use the UPS Time In Transit API? It is slower but delivery dates are more accurate."),
        default=False),

    StringValue(SHIPPING_GROUP,
        'PICKUP_TYPE',
        description=_("UPS Pickup option."),
        choices = (
            (('01', 'DAILY PICKUP')),
            (('03', 'CUSTOMER COUNTER')),
            (('06', 'ONE TIME PICKUP')),
            (('07', 'ON CALL PICKUP')),
            ),
        default = u"07"),

    BooleanValue(SHIPPING_GROUP,
        'LIVE',
        description=_("Access production UPS server"),
        help_text=_("Use this when your store is in production."),
        default=False),

    StringValue(SHIPPING_GROUP,
        'CONNECTION',
        description=_("Submit to URL"),
        help_text=_("Address to submit live transactions."),
        default="https://onlinetools.ups.com/ups.app/xml/Rate"),

    StringValue(SHIPPING_GROUP,
        'CONNECTION_TEST',
        description=_("Submit to TestURL"),
        help_text=_("Address to submit test transactions."),
        default="https://wwwcie.ups.com/ups.app/xml/Rate"),

    BooleanValue(SHIPPING_GROUP,
        'VERBOSE_LOG',
        description=_("Verbose logs"),
        help_text=_("Send the entire request and response to the log - for debugging help when setting up UPS."),
        default=False)

)
