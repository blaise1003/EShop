from decimal import Decimal
from django.core import urlresolvers
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import never_cache
from livesettings import config_get_group, config_value 
from payment.config import gateway_live
from payment.utils import get_processor_by_key
from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order
from satchmo_utils.dynamic import lookup_url, lookup_template
import logging
from satchmo_utils.views import bad_or_missing

from satchmoutils.payments.modules.creditcard.GestPayCrypt import GestPayCrypt
from satchmoutils.payments.modules.views import pay_ship_info_view_wrapper

log = logging.getLogger()


pay_ship_info = pay_ship_info_view_wrapper('creditcard')

def confirm_info(request):
    payment_module = config_get_group('PAYMENT_CREDITCARD')

    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        url = lookup_url(payment_module, 'satchmo_checkout-step1')
        return HttpResponseRedirect(url)

    tempCart = Cart.objects.from_request(request)
    if tempCart.numItems == 0 and not order.is_partially_paid:
        template = lookup_template(
            payment_module, 
            'shop/checkout/empty_cart.html'
        )
        return render_to_response(template,
                                  context_instance=RequestContext(request))

    # Check if the order is still valid
    if not order.validate(request):
        context = RequestContext(request,
                        {'message': _('Your order is no longer valid.')})
        return render_to_response('shop/404.html', context_instance=context)

    template = lookup_template(
        payment_module, 
        'shop/checkout/creditcard/confirm.html'
    )
    if payment_module.LIVE.value:
        log.debug("live order on %s", payment_module.KEY.value)
        url = payment_module.POST_URL.value
        account = payment_module.MERCHANT_ID.value
    else:
        url = payment_module.POST_TEST_URL.value
        account = payment_module.MERCHANT_TEST_ID.value

    try:
        address = lookup_url(payment_module,
            payment_module.RETURN_ADDRESS.value, include_server=True)
    except urlresolvers.NoReverseMatch:
        address = payment_module.RETURN_ADDRESS.value
    
    processor_module = payment_module.MODULE.load_module('processor')
    processor = processor_module.PaymentProcessor(payment_module)
    processor.create_pending_payment(order=order)
    default_view_tax = config_value('TAX', 'DEFAULT_VIEW_TAX') 
  
    recurring = None
    order_items = order.orderitem_set.all()
    for item in order_items:
        if item.product.is_subscription:
            recurring = {
                'product':item.product, 
                'price':item.product.price_set.all()[0].price.quantize(Decimal('.01'))
            }
            trial0 = recurring['product'].subscriptionproduct.get_trial_terms(0)
            if len(order_items) > 1 or trial0 is not None \
                        or recurring['price'] < order.balance:
                recurring['trial1'] = {'price': order.balance,}
                if trial0 is not None:
                    recurring['trial1']['expire_length'] = trial0.expire_length
                    recurring['trial1']['expire_unit'] = trial0.expire_unit[0]
                trial1 = recurring['product'].subscriptionproduct.get_trial_terms(1)
                if trial1 is not None:
                    recurring['trial2']['expire_length'] = trial1.expire_length
                    recurring['trial2']['expire_unit'] = trial1.expire_unit[0]
                    recurring['trial2']['price'] = trial1.price

    gpc = GestPayCrypt()
    
    gpc.SetShopLogin(account)
    gpc.SetShopTransactionID(str(order.id))
    gpc.SetAmount("%.2f" % order.total)

    a = gpc.GetShopLogin()
    b = ''
    if gpc.Encrypt() == None:
        print "Authorization Failed"
    else:
        b = gpc.GetEncryptedString()
             
    encrypt = url
    params = "?a=%s&b=%s" % (a, b)
    
    url = "%s%s" % (encrypt, params)
    
    ctx = RequestContext(request, {
     'order': order,
     'post_url': url,
     'default_view_tax': default_view_tax, 
     'business': account,
     'currency_code': payment_module.CURRENCY_CODE.value,
     'return_address': address,
     'invoice': order.id,
     'subscription': recurring,
     'PAYMENT_LIVE' : gateway_live(payment_module)
    })

    return render_to_response(template, context_instance=ctx)
confirm_info = never_cache(confirm_info)


def success(request):
    """
    The order has been succesfully processed.  
    This can be used to generate a receipt or some other confirmation
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        bad_or_missing_message = 'Your order has already been processed.'
        return bad_or_missing(request, _(bad_or_missing_message))
        
    amount = order.balance
    payment_module = config_get_group('PAYMENT_CREDITCARD')
    processor = get_processor_by_key('PAYMENT_CREDITCARD')
    account = request.GET.get('a', '')
    ecripted_string = request.GET.get('b', '')
    
    gpc = GestPayCrypt()
    gpc.SetShopLogin(account)
    gpc.SetShopTransactionID(str(order.id))
    gpc.SetAmount("%.2f" % order.total)
    gpc.SetEncryptedString(str(ecripted_string))
    
    # if gpc.Decrypt() == 1 --> Transaction is OK
    if gpc.Decrypt() == 1:
        processor.record_payment(
            order = order,
            amount = amount,
            transaction_id = gpc.GetBankTransactionID(),
            reason_code = gpc.GetAuthorizationCode()
        )
        if order.notes is None:
            order.notes = ""
        else:
            order.notes += "\n\n"
        order.save()
        order.add_status(
            status = 'New',
            notes = "Pagato mediante BANCASELLA"
        )
        
        # Make cart empty
        cart = Cart.objects.from_request(request)
        if cart:
            cart.empty()
        
    return render_to_response('shop/checkout/success_creditcard.html',
                              {'order': order,},
                              context_instance=RequestContext(request))
success = never_cache(success)


def error(request):
    """
    The order has been succesfully with errors.
    """
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, _('Your order has already been processed.'))
        
    return render_to_response('shop/checkout/creditcard/error.html',
                              {'order': order,},
                              context_instance=RequestContext(request))
error = never_cache(error)