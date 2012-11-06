from decimal import Decimal

from satchmoutils.payments.modules.views import (OneStepView, 
    one_step_view_wrapper, pay_ship_info_view_wrapper, 
    confirm_info_view_wrapper, ConfirmInfoClass)

import logging

log = logging.getLogger('satchmoutils.payments.modules.contrassegno')

class ContrassegnoView(OneStepView):

    def preprocess_order(self, order):
        super(ContrassegnoView, self).preprocess_order(order)
        order.shipping_cost += Decimal(
            self.payment_module.HANDLING_COST.value
        )
        order.total += Decimal(
            self.payment_module.HANDLING_COST.value
        )

class ConfirmContrassegnoView(ConfirmInfoClass):
        
    def preprocess_order(self, order):
        super(ContrassegnoView, self).preprocess_order(order)
        order.shipping_cost += Decimal(
            self.payment_module.HANDLING_COST.value
        )
        order.total += Decimal(
            self.payment_module.HANDLING_COST.value
        )

one_step = one_step_view_wrapper('contrassegno', ContrassegnoView)
pay_ship_info = pay_ship_info_view_wrapper('contrassegno')
confirm_info = confirm_info_view_wrapper(
    'contrassegno', 
    ConfirmContrassegnoView
)
# confirm_info = confirm_info_view_wrapper('contrassegno')