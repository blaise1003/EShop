from livesettings import *
from django.utils.translation import ugettext_lazy as _

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_CREDITCARD', 
    _('Payment Credit card Module Settings thru BancaSella'), 
    ordering = 100)

config_register_list(    
    BooleanValue(PAYMENT_GROUP, 
        'LIVE', 
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False),
        
    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description=_('Implementation module'),
        hidden=True,
        default = 'satchmoutils.payments.modules.creditcard'),
        
    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module key"),
        hidden=True,
        default = 'CREDITCARD'),

    BooleanValue(PAYMENT_GROUP,
        'SSL',
        description=_("Use SSL for the checkout pages?"),
        default=True),
        
    StringValue(PAYMENT_GROUP,
        'CURRENCY_CODE',
        description=_('Currency Code'),
        help_text=_('Currency code for transactions (242 = EUR).'),
        default = '242'),
            
    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = _('Creditcard (Bancasella)'),
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = '^creditcard/'),
        
    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False),
    
    StringValue(PAYMENT_GROUP,
        'POST_URL',
        description=_('Post URL '),
        help_text=_('The BancaSella URL for real transaction posting.'),
        default="https://ecomm.sella.it/gestpay/pagam.asp"),

    StringValue(PAYMENT_GROUP,
        'POST_TEST_URL',
        description=_('Post URL TEST'),
        help_text=_('The BancaSella URL for test transaction posting.'),
        default="https://testecomm.sella.it/gestpay/pagam.asp"),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_ID',
        description=_('Merchant ID'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_KEY',
        description=_('Merchant Key'),
        default=""),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_TEST_ID',
        description=_('Merchant Test ID'),
        default="GESPAY49406"),

    StringValue(PAYMENT_GROUP,
        'MERCHANT_TEST_KEY',
        description=_('Merchant Test Key'),
        default="biagio1003"),

    StringValue(PAYMENT_GROUP,
        'RETURN_ADDRESS',
        description=_('Return URL'),
        help_text=_('Where BancaSella will return the customer after the purchase is complete.  This can be a named url and defaults to the standard checkout success.'),
        default="CREDITCARD_satchmo_checkout-success"),
)
