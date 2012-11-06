from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.utils.translation import ugettext_lazy as _

from satchmo_store.shop.models import Config, Cart, Contact
from satchmo_utils.dynamic import lookup_url, lookup_template
from satchmo_utils.views import bad_or_missing
from satchmo_store.shop.models import Order
from payment.views.payship import (base_pay_ship_info, 
                                        simple_pay_ship_process_form)
from payment.views.confirm import ConfirmController

from livesettings import config_get_group, config_value
from payment.utils import get_processor_by_key, get_or_create_order


class BaseViewClass(object):
    
    def __init__(self, processor):
        self.payment_module = config_get_group('PAYMENT_%s' \
                                                    % processor.upper())
        self.processor = get_processor_by_key('PAYMENT_%s' \
                                                    % processor.upper())
        self.processor_configuration = config_get_group('PAYMENT_%s' \
                                                    % processor.upper())
        self._postprocess_callables = []
        
    def preprocess_order(self, order):
        pass
        
    def postprocess_order(self, order):
        for postprocess in self._postprocess_callables:
            postprocess(order)
            
    def __call__(self, request):
        pass
        
class OneStepView(object):

    def __init__(self, processor):
        self.payment_module = config_get_group('PAYMENT_%s' \
                                            % processor.upper())
        self.processor = get_processor_by_key('PAYMENT_%s' \
                                            % processor.upper())
        self._postprocess_callables = []

    def preprocess_order(self, order):
        pass

    def postprocess_order(self, order):
        for postprocess in self._postprocess_callables:
            postprocess(order)

    def __call__(self, request):
        #First verify that the customer exists
        try:
            contact = Contact.objects.from_request(request, create=False)
        except Contact.DoesNotExist:
            url = lookup_url(self.payment_module, 'satchmo_checkout-step1')
            return HttpResponseRedirect(url)
        #Verify we still have items in the cart
        tempCart = Cart.objects.from_request(request)
        if tempCart.numItems == 0:
            template = lookup_template(
                self.payment_module,
                'shop/checkout/empty_cart.html'
            )
            return render_to_response(
                template, context_instance=RequestContext(request)
            )
            
        data = {}
        if request.method == 'POST':
            data['discount'] = request.post.get('discount_code')
        
        
        success = lookup_url(
            self.payment_module,
            '%s_satchmo_checkout-success' % self.processor.key,
        )
        
        order = get_or_create_order(request, tempCart, contact, data)
        
        self.preprocess_order(order)
        
        # Add status
        order.add_status('New', _("Payment needs to be confirmed"))
        # Process payment
        self.processor.prepare_data(order)
        self.processor.process(order)
        tempCart.empty()

        self.postprocess_order(order)
        order.save()

        return HttpResponseRedirect(success)


def one_step_view_wrapper(processor, klass=OneStepView):
    return never_cache(klass(processor))

# Override for allow_skip = False
def noskip_simple_pay_ship_process_form(request, contact, 
        working_cart, payment_module, allow_skip=False):
    return simple_pay_ship_process_form(request, contact, 
            working_cart, payment_module, allow_skip=False)
        
class PayshipInfoClass(BaseViewClass):
    
    def __call__(self, request):
        processor_key = self.processor_configuration.KEY.value.lower()
        template = 'shop/checkout/%s/pay_ship.html' % processor_key
        return base_pay_ship_info(request, self.processor_configuration, 
            noskip_simple_pay_ship_process_form, template)
            
def pay_ship_info_view_wrapper(processor, klass=PayshipInfoClass):
    return never_cache(klass(processor))
    
class ConfirmInfoClass(BaseViewClass):
    
    def __call__(self, request):
        processor_key = self.processor_configuration.KEY.value.lower()
        template = 'shop/checkout/%s/confirm.html' % processor_key
        
        controller = ConfirmController(request, self.payment_module)
        
        controller.templates['CONFIRM'] = template
        
        controller.confirm()
        
        return controller.response

def confirm_info_view_wrapper(processor, klass=ConfirmInfoClass):
    return never_cache(klass(processor))
    
def multisuccess_view(request):
    """
    The order has been succesfully processed.  
    This can be used to generate a receipt or some other confirmation
    """
    
    target_view = None
    
    try:
        order = Order.objects.from_request(request)
    except Order.DoesNotExist:
        return bad_or_missing(request, 
            _('Your order has already been processed.'))
        
    del request.session['orderID']
    payments_completed = order.payments_completed()
    if payments_completed:
        payment_completed = payments_completed[0].payment
    else:
        payment_completed = ''
    
    shop = Config.objects.get_current()
    postal_code = shop.postal_code
    city = shop.city
    phone = shop.phone
    fax = ""
    store_email = shop.store_email
    store_name = shop.store_name
    street1 = shop.street1
    state = shop.state
    p_iva = config_value('SHOP_CONFIG','VAT')
    iban = config_value('SHOP_CONFIG','IBAN')
    
    # Cablare il campo per il rilevamento della tipologia 
    # di pagamento
    target_view = []
    if payment_completed:
        target_view.append(
            "shop/checkout/success_%s.html" % payment_completed.lower()
        )
    target_view.append("shop/checkout/success_generic.html")
    
    return render_to_response(
          target_view,
          {
              'order': order,
              'payment': payment_completed,
              'p_iva' : p_iva,
              'iban' : iban,
              'store_postal_code' : postal_code,
              'store_phone' : phone,
              'store_fax' : fax,
              'store_email' : store_email,
              'store_name' : store_name,
              'store_street1' : street1,
              'store_state' : state,
              'store_city' : city,
          },
          context_instance=RequestContext(request)
    )
    
multisuccess_view = never_cache(multisuccess_view)
