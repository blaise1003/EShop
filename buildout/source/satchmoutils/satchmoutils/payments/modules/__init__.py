from payment.signals import payment_methods_query
from livesettings import config_get_group

def get_processor_by_key(key):
    """
    Returns an instance of a payment processor, referred to by *key*.

    :param key: A string of the form 'PAYMENT_<PROCESSOR_NAME>'.
    """
    payment_module = config_get_group('PAYMENT_%s' % key)
    processor_module = payment_module.MODULE.load_module('processor')
    return processor_module.PaymentProcessor(payment_module)
    
def filtering_handler(sender, **kwargs):
    methods = kwargs['methods']
    cart = kwargs['cart']
    deletion_list = []
    for i in xrange(0, len(methods)):
        processor = get_processor_by_key(methods[i][0])
        allowed_for = True
        if hasattr(processor, 'allowed_for'):
            allowed_for = processor.allowed_for(cart)
        if not allowed_for:
            deletion_list.append(methods[i][0])
    for index in deletion_list:
        i = 0
        for method in methods:
            if index == method[0]:
                del methods[i]
            i += 1

payment_methods_query.connect(filtering_handler)