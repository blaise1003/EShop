# -*- coding: utf-8 -*-
from livesettings import config_register, ConfigurationGroup, StringValue
from django.utils.translation import ugettext_lazy as _

from product.models import Category

from .utils import ModelValue


# GIFT_INFO configs
GIFT_INFO = ConfigurationGroup(
    'GIFT_INFO',
    _('Gift configurations'),
    ordering=0
    )

# Codice univoco
config_register(
    StringValue(
        GIFT_INFO,
        'LABEL',
        description = _('Label for gift orders annotation'),
        help_text = "",
        default = "Is a gift."
    )
)

# Gift category
config_register(
    ModelValue(
        GIFT_INFO,
        'GIFT_CATEGORY',
        description=_(u'Gift Category'),
        help_text=_(u"Choose which category contains gift products"),
        queryset = Category.objects.all(),
        required=False
    )
)