from django import http
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core import urlresolvers
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.forms.models import model_to_dict
from django.utils.translation import ugettext
from satchmo_store.contact import signals, CUSTOMER_ID
from satchmo_store.contact.forms import ExtendedContactInfoForm, ContactInfoForm, area_choices_for_country, AddressBookForm, YesNoForm
from satchmo_store.contact.models import Contact, AddressBook
from satchmo_store.shop.models import Config
import logging
from django.utils.translation import ugettext, ugettext_lazy as _

log = logging.getLogger('satchmo_store.contact.views')

def view(request):
    """View contact info."""
    try:
        user_data = Contact.objects.get(user=request.user.id)
    except Contact.DoesNotExist:
        user_data = None

    contact_dict = {
        'user_data': user_data,
    }

    signals.satchmo_contact_view.send(user_data, contact=user_data, contact_dict=contact_dict)

    context = RequestContext(request, contact_dict)

    return render_to_response('contact/view_profile.html',
                              context_instance=context)

view = login_required(view)

def update(request):
    """Update contact info"""

    init_data = {}
    shop = Config.objects.get_current()

    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None


    if request.method == "POST":
        new_data = request.POST.copy()
        form = ExtendedContactInfoForm(data=new_data, shop=shop, contact=contact, shippable=True,
            initial=init_data)

        if form.is_valid():
            if contact is None and request.user:
                contact = Contact(user=request.user)
            custID = form.save(contact=contact)
            request.session[CUSTOMER_ID] = custID
            redirect_to = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = urlresolvers.reverse('satchmo_account_info')

            return http.HttpResponseRedirect(redirect_to)
        else:
            signals.satchmo_contact_view.send(contact, contact=contact, contact_dict=init_data)

    else:
        if contact:
            #If a person has their contact info, make sure we populate it in the form
            for item in contact.__dict__.keys():
                init_data[item] = getattr(contact,item)
            if contact.shipping_address:
                for item in contact.shipping_address.__dict__.keys():
                    init_data["ship_"+item] = getattr(contact.shipping_address,item)
            if contact.billing_address:
                for item in contact.billing_address.__dict__.keys():
                    init_data[item] = getattr(contact.billing_address,item)
            if contact.primary_phone:
                init_data['phone'] = contact.primary_phone.phone
            if contact.organization:
                init_data['organization'] = contact.organization.name
        else:
            #If a person has no contact info, try to get some from its user account
            if request.user:
                for field in ('email', 'first_name', 'last_name'):
                    if getattr(request.user, field, False):
                        init_data[field] = getattr(request.user, field)


        signals.satchmo_contact_view.send(contact, contact=contact, contact_dict=init_data)
        form = ExtendedContactInfoForm(shop=shop, contact=contact, shippable=True, initial=init_data)

    init_data['form'] = form
    if shop.in_country_only:
        init_data['country'] = shop.sales_country
    else:
        countries = shop.countries()
        if countries and countries.count() == 1:
            init_data['country'] = countries[0]


    init_data['next'] = request.REQUEST.get(REDIRECT_FIELD_NAME, '')
    context = RequestContext(request, init_data)

    return render_to_response('contact/update_form.html',
                              context_instance=context)

update = login_required(update)


def address_create_edit(request, id=None):
    """Create and edit new address book entries
    """
    initial_entry = None
    initial_data = {}
    editing = False
    next_url = request.GET.get('next',None)
    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None
    if id:
        initial_entry = get_object_or_404(AddressBook, pk=id)
        # Make sure we only edit entries associated with this contact
        if initial_entry.contact <> contact:
            return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_account_info'))
        initial_data = model_to_dict(initial_entry, fields=[], exclude=['contact'])
        # This is a bit of a hack because we normally use jquery to populate the addressee
        initial_data['addressee_name'] = initial_data["addressee"]
    if request.method == 'POST':
        form = AddressBookForm(request.POST)
        if form.is_valid():
            form.save(contact, address_entry=initial_entry)
            messages.success(request, _('Succcessfully saved addressbook changes.'))
            if next_url:
                return http.HttpResponseRedirect(next_url)
            else:
                return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_account_info'))
    else:
        form = AddressBookForm(initial=initial_data)
    if initial_entry:
        editing = True
    context = RequestContext(request, {'form':form, 'editing':editing, 'entry':initial_entry, 'next':next_url})    
    return render_to_response('contact/address_form.html',context_instance=context)
address_create_edit = login_required(address_create_edit)

def address_delete(request, id=None):
    """Delete an addressbook entry
    """
    initial_entry = None
    try:
        contact = Contact.objects.from_request(request, create=False)
    except Contact.DoesNotExist:
        contact = None
    if id:
        initial_entry = get_object_or_404(AddressBook, pk=id)
        # Make sure we only edit entries associated with this contact
        if initial_entry.contact <> contact:
            return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_account_info'))
    if request.method == 'POST' and initial_entry:
        if request.POST['delete_entry'] == 'Yes':
            initial_entry.delete()
        return http.HttpResponseRedirect(urlresolvers.reverse('satchmo_account_info'))
    else:
        form = YesNoForm()
    context = RequestContext(request, {'form':form,'entry':initial_entry})    
    return render_to_response('contact/address_form_delete.html',context_instance=context)
address_delete = login_required(address_delete)


class AjaxGetStateException(Exception):
    """Used to barf."""
    def __init__(self, message):
        self.message = message

def ajax_get_state(request, **kwargs):
    formdata = request.REQUEST.copy()

    try:
        if formdata.has_key("country"):
            country_field = 'country'
        elif formdata.has_key("ship_country"):
            country_field = 'ship_country'
        else:
            raise AjaxGetStateException("No country specified")

        form = ContactInfoForm(data=formdata)
        country_data = formdata.get(country_field)
        try:
            country_obj = form.fields[country_field].clean(country_data)
        except:
            raise AjaxGetStateException("Invalid country specified")

        areas = area_choices_for_country(country_obj, ugettext)

        context = RequestContext(request, {
            'areas': areas,
        })
        return render_to_response('contact/_state_choices.html',
                                  context_instance=context)
    except AjaxGetStateException, e:
        log.error("ajax_get_state aborting: %s" % e.message)

    return http.HttpResponseServerError()
