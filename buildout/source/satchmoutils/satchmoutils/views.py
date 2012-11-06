#!/usr/bin/env python
from django import forms
from django import http
from django.core import urlresolvers
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import DetailView
from satchmo_store.mail import send_store_mail
from satchmo_store.shop.signals import contact_sender
from satchmo_store.shop.views.contact import ContactForm as BaseContactForm
from satchmo_store.shop.models import Cart

from captcha.fields import CaptchaField
from .models import Page

import logging


log = logging.getLogger('primifrutti.ui.views')


# Make Emty Cart View
def cart_empty(request):
    """
    make empty current cart
    """
    cart = Cart.objects.from_request(request, create=True)

    # make cart empty
    cart.empty()
    return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_cart'))


# Choices displayed to the user to categorize the type of contact request.
email_choices = (
    ("General Question", _(u"General question")),
    ("Order Problem", _(u"Order problem")),
    ("Product Info", _(u"Product Info")),
    ("Shipping Info", _(u"Shipping Info")),
)


class ContactForm(BaseContactForm):
    inquiry = forms.ChoiceField(label=_("Inquiry"), choices=email_choices,
        help_text=_(u"What about yuor question"))
    captcha = CaptchaField(required=True,
        help_text=_(u"Insert word you see into image"))


def contact_form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            new_data = form.cleaned_data
            c = {
                'request_type': new_data['inquiry'],
                'name': new_data['name'],
                'email': new_data['sender'],
                'request_text': new_data['contents']}
            subject = new_data['subject']
            send_store_mail(subject, c, 'shop/email/contact_us.txt',
                            send_to_store=True, sender=contact_sender)
            url = urlresolvers.reverse('satchmo_contact_thanks')
            return http.HttpResponseRedirect(url)
    else: #Not a post so create an empty form
        initialData = {}
        if request.user.is_authenticated():
            initialData['sender'] = request.user.email
            initialData['name'] = request.user.first_name + " " + \
                                                    request.user.last_name
        form = ContactForm(initial=initialData)

    return render_to_response('shop/contact_form.html', {'form': form},
                              context_instance=RequestContext(request))


class PageView(DetailView):
    """ display static page item
    """
    model = Page
    slug_field = 'slug'
    context_object_name = "page"
    template_name = 'shop/page.html'


get_static_page = PageView.as_view()
