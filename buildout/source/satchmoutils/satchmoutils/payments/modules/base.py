from django.utils.translation import ugettext_lazy as _
from payment.modules.base import BasePaymentProcessor, ProcessorResult

class BaseProcessor(BasePaymentProcessor):
    method_name = ''
        
    def allowed_for(self, cart=None):
        """Allows different payment processors to be allowed for certain situations."""
        return True
        
class OneStepBasePaymentProcessor(BaseProcessor):
    method_name = ''

    def __init__(self, settings):
        super(OneStepBasePaymentProcessor, self).__init__(
            self.method_name, settings
        )

    def capture_payment(self, testing=False, order=None, amount=None):
        if not order:
            order = self.order

        if amount is None:
            amount = order.balance

        payment = self.record_payment(
            order=order,
            amount=amount,
            transaction_id="%s-ORDER-#%s" % (
                self.method_name.upper(),
                order.pk
            ),
            reason_code='0')

        return ProcessorResult(self.key, True, _('Success'), payment)