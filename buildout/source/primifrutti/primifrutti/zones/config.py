# -*- coding: utf-8 -*-
from decimal import Decimal
from livesettings import (config_register, ConfigurationGroup,
                                    StringValue, DecimalValue)
from django.utils.translation import ugettext_lazy as _


# ZONES_INFO configs
ZONES_INFO = ConfigurationGroup(
    'ZONES_INFO',
    _('Configurations for Zones'),
    ordering=0
)

# max_days
config_register(
    DecimalValue(
        ZONES_INFO,
        'MAX_DAYS',
        description=_('Max days for stale shipments'),
        help_text="",
        default=Decimal('1'),
    )
)