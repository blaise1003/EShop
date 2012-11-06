from satchmoutils.payments.modules.base import OneStepBasePaymentProcessor


class PaymentProcessor(OneStepBasePaymentProcessor):
    """Contrassegno Payment Module
    """

    method_name = 'contrassegno'
