from satchmoutils.payments.modules.views import (OneStepView, 
    one_step_view_wrapper, confirm_info_view_wrapper, 
    pay_ship_info_view_wrapper)

import logging

log = logging.getLogger('satchmoutils.payments.modules.bonifico.views')


class BonificoView(OneStepView):

    def preprocess_order(self, order):
        super(BonificoView, self).preprocess_order(order)
        # update order status
        order.add_status(
            status='New', 
            notes="Attesa di pagamento a mezzo bonifico"
        )
        
one_step = one_step_view_wrapper('bonifico', BonificoView)
pay_ship_info = pay_ship_info_view_wrapper('bonifico')
confirm_info = confirm_info_view_wrapper('bonifico')