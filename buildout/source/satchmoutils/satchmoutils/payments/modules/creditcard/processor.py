from payment.modules.base import HeadlessPaymentProcessor
from satchmoutils.payments.modules.base import BaseProcessor

class PaymentProcessor(BaseProcessor, HeadlessPaymentProcessor):
    """Credit Card Payment Module with BancaSella
    """

    method_name = 'creditcard'
    
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('creditcard', settings)