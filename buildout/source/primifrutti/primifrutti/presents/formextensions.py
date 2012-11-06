# -*- coding: utf-8 -*-
import logging
from django import forms
from livesettings import config_value
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.forms.fields import BooleanField
from payment.forms import PaymentContactInfoForm

from satchmo_store.shop.models import Order

log = logging.getLogger('primifrutti.presents.forms')

from satchmoutils.formextender import Extender, ExtraField, Fieldset

def clean_is_gift(self):
    is_gift = self.cleaned_data.get('is_gift', False)
    copy_address = self.cleaned_data.get('copy_address', False)
    if is_gift and copy_address:
        raise ValidationError(
            message = _(
                u"You must specify different shipping address for this gift"
            ),
            code = 'invalid'
        )
    else:
        return is_gift


class CheckoutGiftExtender(Extender):
    extends = (PaymentContactInfoForm,)
    fieldsets = [
        Fieldset(
            'other',
            _(u'Other informations'),
            ('is_gift',)
        ),
    ]
    methods = {
        'clean_is_gift' : clean_is_gift,
    }
    
    @classmethod
    def get_fields(cls):
        return [
            ExtraField(
                BooleanField,
                name='is_gift',
                css_class='',
                label = _(u"Is this a gift?"),
                widget = forms.CheckboxInput(),
                required = False
            )
        ]

    @classmethod
    def handle_postsave(cls, **kwargs):
        try:
            form = kwargs['form']
            order = form.order
        except Order.DoesNotExist, e:
            logging.warning("The form save handler is missing something: %s" % e)
        else:
            is_gift_msg = config_value('GIFT_INFO', 'LABEL')
            if (not order.notes) and ('is_gift' in form.data.keys()):
                order.notes = is_gift_msg
                order.save()
