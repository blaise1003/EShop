from django.utils.translation import ugettext_lazy as _
from livesettings import * 
from tax.config import TAX_MODULE


TAX_MODULE.add_choice(('satchmoutils.tax.modules.noarea', _('No Area Tax')))
TAX_GROUP = config_get_group('TAX')


config_register(
     BooleanValue(TAX_GROUP,
         'TAX_SHIPPING',
         description=_("Tax Shipping?"),
         requires=TAX_MODULE,
         requiresvalue='satchmoutils.tax.modules.noarea',
         default=False)
)

config_register(
     StringValue(TAX_GROUP,
         'TAX_CLASS',
         description=_("TaxClass for shipping"),
         help_text=_("Select a TaxClass that should be applied for shipments."),
         default='Shipping'
     )
)

config_register(
     BooleanValue(TAX_GROUP,
         'TAX_USE_ITEMPRICE',
         description=_("Use item full-price for tax?"),
         requires=TAX_MODULE,
         requiresvalue='satchmoutils.tax.modules.noarea',
         default=True)
)
