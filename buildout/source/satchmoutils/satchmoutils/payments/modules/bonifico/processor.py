from satchmoutils.payments.modules.base import OneStepBasePaymentProcessor


class PaymentProcessor(OneStepBasePaymentProcessor):
    """Bonifico Payment Module
    """

    method_name = 'bonifico'