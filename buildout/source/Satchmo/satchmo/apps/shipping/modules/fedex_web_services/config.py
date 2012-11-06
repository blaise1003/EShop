"""
Satchmo Fedex Module that uses Fedex Web Services via the SOAP protoccol.
This is based on several people's work.
  - https://github.com/jcartmell/python-fedex which was forked from
  - https://github.com/gtaylor/python-fedex
  - Some inspiration drawn from fedex shipping module by Chris Laux
  - Some was drawn from the python-fedex examples
  
This requires 2 additional modules to work:
Python Fedex and the Python SOAP module suds.
http://code.google.com/p/python-fedex/
https://fedorahosted.org/suds/

Both can be installed easily:
pip install fedex
pip install suds

All values based on July 2011 Fedex Developer Guide
"""

from django.utils.translation import ugettext_lazy as _
from livesettings import *
SHIP_MODULES = config_get('SHIPPING', 'MODULES')
SHIP_MODULES.add_choice(('shipping.modules.fedex_web_services', 'FEDEX (fedex_web_services)'))

SHIPPING_GROUP = ConfigurationGroup('shipping.modules.fedex_web_services',
  _('FedEx Web Services Shipping Settings'),
  requires = SHIP_MODULES,
  requiresvalue='shipping.modules.fedex_web_services',
  ordering = 101
)

config_register_list(

    StringValue(SHIPPING_GROUP,
        'METER_NUMBER',
        description=_('FedEx Meter Number'),
        help_text=_('Meter Number provided by FedEx.'),
        default=u''),
    
    StringValue(SHIPPING_GROUP,
        'ACCOUNT',
        description=_('FedEx Account Number'),
        help_text=_('FedEx Account Number.'),
        default=u''),
    
    StringValue(SHIPPING_GROUP,
        'AUTHENTICATION_KEY',
        description=_('FedEx Authentication Key'),
        help_text=_('FedEx Authentication Key.'),
        default=u''),
    
    StringValue(SHIPPING_GROUP,
        'AUTHENTICATION_PASSWORD',
        description=_('FedEx Authentication Password'),
        help_text=_('FedEx Authentication Password.'),
        default=u''),
    
    StringValue(SHIPPING_GROUP,
        'SHIPPER_REGION',
        description=_('The region you are sending your package from.'),
        help_text=_('i.e. the region the package leaves from.'),
        choices = (
            ('APAC',  'APAC'),
            ('CA',  'CA'),
            ('EMEA',       'EMEA'),
            ('LAC',  'LAC'),
            ('US',       'US'),
        ),
        default = 'US',
    ),
    
    MultipleStringValue(SHIPPING_GROUP,
        'SHIPPING_CHOICES',
        description=_('FedEx Shipping Choices Available to customers.'),
        choices = (
            ('EUROPE_FIRST_INTERNATIONAL_PRIORITY', 'Europe First International Priority'),
            ('FEDEX_1_DAY_FREIGHT',             'Fedex 1 Day Freight'),
            ('FEDEX_2_DAY',                     'Fedex 2 Day'),
            ('FEDEX_2_DAY_FREIGHT',             'Fedex 2 Day Freight'),
            ('FEDEX_3_DAY_FREIGHT',             'Fedex 3 Day Freight'),
            ('FEDEX_EXPRESS_SAVER',             'Fedex Express Saver'),
            ('FEDEX_GROUND',                    'Fedex Ground'),
            ('FIRST_OVERNIGHT',                 'First Overnight'),
            ('GROUND_HOME_DELIVERY',            'Ground Home Delivery'),
            ('INTERNATIONAL_ECONOMY',           'International Economy'),
            ('INTERNATIONAL_ECONOMY_FREIGHT',   'International Economy Freight'),
            ('INTERNATIONAL_FIRST',             'International First'),
            ('INTERNATIONAL_PRIORITY',          'International Priority'),
            ('INTERNATIONAL_PRIORITY_FREIGHT',  'International Priority Freight'),
            ('PRIORITY_OVERNIGHT',              'Priority Overnight'),
            ('SMART_POST',                      'Smart Post'),
            ('STANDARD_OVERNIGHT',              'Standard Overnight'),
            ('FEDEX_FREIGHT',                   'Fedex Freight'),
            ('FEDEX_NATIONAL_FREIGHT',          'Fedex National Freight'),
            ('INTERNATIONAL_GROUND',            'International Ground'),
        ),
        default = 'FEDEX_GROUND'
        ),

    StringValue(SHIPPING_GROUP,
        'PACKAGING',
        description = _('Type of container/package used to ship product.'),
        choices = (
            ('YOUR_PACKAGING','YOUR_PACKAGING'),
            ('FEDEX_10KG_BOX','FEDEX_10KG_BOX'),
            ('FEDEX_25KG_BOX','FEDEX_25KG_BOX'),
            ('FEDEX_BOX','FEDEX_BOX'),
            ('FEDEX_ENVELOPE','FEDEX_ENVELOPE'),
            ('FEDEX_PAK','FEDEX_PAK'),
            ('FEDEX_TUBE','FEDEX_TUBE'),
        ),
        default = 'YOUR_PACKAGING',
    ),
    
    StringValue(SHIPPING_GROUP,
        'DEFAULT_ITEM_WEIGHT',
        description = _("Default/Minimum Item Weight"),
        help_text = _("The default weight for items which lack a defined weight and the minimum an item is allowed to be, enter a positive value."),
        default = '0.5',
    ),
    StringValue(SHIPPING_GROUP,
        'DEFAULT_WEIGHT_UNITS',
        description = _("Default weight units"),
        choices = (
                    ('LB','LB'),
                    ('KG','KG'),
                   ),
        default = "LB"
    ),
    
    BooleanValue(SHIPPING_GROUP,
        'SINGLE_BOX',
        description=_("Single Box?"),
        help_text=_("Use just one box and ship by weight?  If no then every item will be sent in its own box."),
        default=True
    ),
    StringValue(SHIPPING_GROUP,
        'DROPOFF_TYPE',
        description = _("The method used to give the package to Fedex."),
         choices = (
            ('REGULAR_PICKUP','REGULAR_PICKUP'),
            ('BUSINESS_SERVICE_CENTER','BUSINESS_SERVICE_CENTER'),
            ('DROP_BOX','DROP_BOX'),
            ('REQUEST_COURIER','REQUEST_COURIER'),
            ('STATION', 'STATION'),
        ),
        help_text = _("Most users will keep the default Regular Pickup."),
        default = 'REGULAR_PICKUP',
    ),
    
    BooleanValue(SHIPPING_GROUP,
        'VERBOSE_LOG',
        description=_("Verbose logs"),
        help_text=_("Send the entire request and response to the log - for debugging help when setting up FedEx."),
        default=False),
    
    BooleanValue(SHIPPING_GROUP,
        'TEST_SERVER',
        description=_("Use test server?"),
        help_text=_("Check if you want to use the fedex test servers rather than the production server."),
        default=True
        ),
)
