####################################################################
# First step in the order process - capture all the demographic info
#####################################################################

import logging
from django import http
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import FormView
from signals_ahoy.signals import form_initialdata
from livesettings import config_get_group, config_value
from satchmo_store.contact import CUSTOMER_ID
from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Cart, Config, Order
from satchmo_utils.dynamic import lookup_url
from payment.decorators import cart_has_minimum_order
from payment.forms import PaymentContactInfoForm

log = logging.getLogger('satchmo_store.contact.contact')

def authentication_required(request, 
    template='shop/checkout/authentication_required.html'):
    return render_to_response(
        template, {}, context_instance = RequestContext(request)
    )


class CheckoutForm(FormView):
    """ rebase contact_info view """
    initial = {}
    template_name = 'shop/checkout/form.html'
    form_class = PaymentContactInfoForm

    def __init__(self, **kwargs):
        self._success_url = None
        self._initial_data = {}
        self._form_extrakwargs = {}
        super(CheckoutForm, self).__init__(**kwargs)

    def get_shop(self):
        shop = Config.objects.get_current()
        return shop

    def get_contact(self):
        try:
            contact = Contact.objects.from_request(self.request, create=False)
        except Contact.DoesNotExist:
            contact = None
        return contact

    def get_order(self):
        try:
            order = Order.objects.from_request(self.request)
        except Order.DoesNotExist:
            order = None
        return order

    def get_cart(self):
        try:
            cart = Cart.objects.from_request(self.request)
        except Cart.DoesNotExist:
            cart = None
        return cart

    def get_form_kwargs(self):
        kwargs = super(CheckoutForm, self).get_form_kwargs()
        kwargs.update(self._form_extrakwargs)
        return kwargs

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        init_data = {}
        if not self.request.user.is_authenticated() and \
                config_value('SHOP', 'AUTHENTICATION_REQUIRED'):
            url = urlresolvers.reverse('satchmo_checkout_auth_required')
            thisurl = urlresolvers.reverse('satchmo_checkout-step1')
            return http.HttpResponseRedirect(url + "?next=" + thisurl)

        if self.request.user.is_authenticated():
            if self.request.user.email:
                init_data['email'] = self.request.user.email
            if self.request.user.first_name:
                init_data['first_name'] = self.request.user.first_name
            if self.request.user.last_name:
                init_data['last_name'] = self.request.user.last_name
        else:
            init_data = {}

        order = self.get_order()
        if order and order.discount_code:
            init_data['discount'] = order.discount_code
        init_data.update(self._initial_data)
        return init_data

    def get_context_data(self, **kwargs):
        kwargs = super(CheckoutForm, self).get_context_data(**kwargs)
        shop = self.get_shop()
        if shop.in_country_only:
            only_country = shop.sales_country
        else:
            only_country = None

        payment_methods = kwargs['form'].fields['paymentmethod'].choices
        kwargs.update({
            'country': only_country,
            'paymentmethod_ct': len(payment_methods)
        })
        return kwargs

    def get_success_url(self):
        if self._success_url is not None:
            return self._success_url
        return super(CheckoutForm, self).get_success_url()

    def get(self, request, *args, **kwargs):
        contact = self.get_contact()
        init_data = self.get_initial()

        if contact:
            # If a person has their contact info, 
            # make sure we populate it in the form
            for item in contact.__dict__.keys():
                init_data[item] = getattr(contact, item)
            if contact.shipping_address:
                for item in contact.shipping_address.__dict__.keys():
                    init_data["ship_"+item] = getattr(
                        contact.shipping_address,
                        item
                    )
            if contact.billing_address:
                for item in contact.billing_address.__dict__.keys():
                    init_data[item] = getattr(contact.billing_address,item)
            if contact.primary_phone:
                init_data['phone'] = contact.primary_phone.phone
        else:
            # Allow them to login from this page.
            request.session.set_test_cookie()

        tempCart = self.get_cart()
        if (not tempCart) or (tempCart.numItems == 0):
            return render_to_response('shop/checkout/empty_cart.html',
                            context_instance=RequestContext(self.request))

        shop = self.get_shop()

        form_initialdata.send(
            sender=self.get_form_class(),
            initial=init_data,
            contact=contact,
            cart=tempCart,
            shop=shop
        )
        self._initial_data = init_data

        self._form_extrakwargs['shop'] = shop
        self._form_extrakwargs['contact'] = contact
        self._form_extrakwargs['shippable'] = tempCart.is_shippable
        self._form_extrakwargs['cart'] = tempCart

        return super(CheckoutForm, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        contact = self.get_contact()
        new_data = self.request.POST.copy()
        tempCart = self.get_cart()

        if contact is None and self.request.user \
            and self.request.user.is_authenticated():
            contact = Contact(user=self.request.user)
        custID = form.save(self.request, cart=tempCart, contact=contact)
        self.request.session[CUSTOMER_ID] = custID

        modulename = new_data['paymentmethod']
        if not modulename.startswith('PAYMENT_'):
            modulename = 'PAYMENT_' + modulename
        paymentmodule = config_get_group(modulename)
        url = lookup_url(paymentmodule, 'satchmo_checkout-step2')
        self._success_url = url
        return super(CheckoutForm, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated() and \
                config_value('SHOP', 'AUTHENTICATION_REQUIRED'):
            url = urlresolvers.reverse('satchmo_checkout_auth_required')
            thisurl = urlresolvers.reverse('satchmo_checkout-step1')
            return http.HttpResponseRedirect(url + "?next=" + thisurl)
            
        tempCart = self.get_cart()
        new_data = self.request.POST.copy()

        if not tempCart.is_shippable:
            new_data['copy_address'] = True
        self._form_extrakwargs['data'] = new_data
        self._form_extrakwargs['shop'] = self.get_shop()
        self._form_extrakwargs['contact'] = self.get_contact()
        self._form_extrakwargs['shippable'] = tempCart.is_shippable
        self._form_extrakwargs['cart'] = tempCart

        return super(CheckoutForm, self).post(request, *args, **kwargs)


contact_info = CheckoutForm.as_view()
contact_info_view = cart_has_minimum_order()(contact_info)
