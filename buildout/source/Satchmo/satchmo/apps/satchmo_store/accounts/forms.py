from django import forms
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext_lazy as _, ugettext
from satchmo_store.accounts.mail import send_welcome_email
from livesettings import config_value
from satchmo_store.contact.forms import ContactInfoForm
from satchmo_store.contact.models import Contact, ContactRole
from satchmo_utils.unique_id import generate_id
from signals_ahoy.signals import form_init, form_initialdata

import logging
import signals

# I put this on all required fields, because it's easier to pick up
# on them with CSS or JavaScript if they have a class of "required"
# in the HTML. Your mileage may vary. If/when Django ticket #3515
# lands in trunk, this will no longer be necessary.

attrs_dict = { 'class': 'required' }
log = logging.getLogger('accounts.forms')

class EmailAuthenticationForm(AuthenticationForm):
    """Authentication form with a longer username field."""
    username = forms.CharField(label=_("Username"), max_length=75)

class RegistrationForm(forms.Form):
    """The basic account registration form."""
    title = forms.CharField(max_length=30, label=_('Title'), required=False)
    email = forms.EmailField(label=_('Email address'),
        max_length=75, required=True)
    password2 = forms.CharField(label=_('Password (again)'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    password1 = forms.CharField(label=_('Password'),
        max_length=30, widget=forms.PasswordInput(), required=True)
    first_name = forms.CharField(label=_('First name'),
        max_length=30, required=True)
    last_name = forms.CharField(label=_('Last name'),
        max_length=30, required=True)
    next = forms.CharField(max_length=200, required=False, widget=forms.HiddenInput())
    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                required=False,
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_(u'Username'),
                                error_messages={'invalid':_('Please use only letters, numbers and @/./+/-/_')})


    def __init__(self, *args, **kwargs):
        contact = kwargs.get('contact', None)
        initial = kwargs.get('initial', {})
        self.contact = contact
        form_initialdata.send(RegistrationForm,
            form=self,
            contact=contact,
            initial=initial)

        kwargs['initial'] = initial
        super(RegistrationForm, self).__init__(*args, **kwargs)
        form_init.send(RegistrationForm,
            form=self,
            contact=contact)

    newsletter = forms.BooleanField(label=_('Newsletter'),
        widget=forms.CheckboxInput(), required=False)

    def clean_password1(self):
        """Enforce that password and password2 are the same."""
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if not (p1 and p2 and p1 == p2):
            raise forms.ValidationError(
                ugettext("The two passwords do not match."))

        # note, here is where we'd put some kind of custom
        # validator to enforce "hard" passwords.
        return p1

    def clean_username(self):
        """Validate username is unique
        """
        username = self.cleaned_data.get('username',None)
        if username and User.objects.filter(username__iexact=username).count() > 0:
            raise forms.ValidationError(
                ugettext("That username is already in use."))
        return username

    def clean_email(self):
        """Prevent account hijacking by disallowing duplicate emails."""
        email = self.cleaned_data.get('email', None)
        if email and User.objects.filter(email__iexact=email).count() > 0:
            raise forms.ValidationError(
                ugettext("That email address is already in use."))

        return email

    def save(self, request=None, force_new=False, **kwargs):
        """Create the contact and user described on the form.  Returns the
        `contact`.
        """
        if self.contact:
            log.debug('skipping save, already done')
        else:
            self.save_contact(request, force_new_contact = force_new)

        return self.contact

    def save_contact(self, request, force_new_contact = False):
        log.debug("Saving contact")
        data = self.cleaned_data
        password = data['password1']
        email = data['email']
        first_name = data['first_name']
        last_name = data['last_name']
        allow_nickname = config_value('SHOP', 'ALLOW_NICKNAME_USERNAME')
        if allow_nickname and data['username']:
            username = data['username']
        else:
            username = generate_id(first_name, last_name, email)
        verify = (config_value('SHOP', 'ACCOUNT_VERIFICATION') == 'EMAIL')

        if verify:
            site = Site.objects.get_current()
            from registration.models import RegistrationProfile
            # TODO:
            # In django-registration trunk this signature has changed.
            # Satchmo is going to stick with the latest release so I'm changing
            # this to work with 0.7
            # When 0.8 comes out we're going to have to refactor to this:
            #user = RegistrationProfile.objects.create_inactive_user(
            #    username, email, password, site)
            # See ticket #1028 where we checked in the above line prematurely
            user = RegistrationProfile.objects.create_inactive_user(username,
                    email, password, site)
        else:
            user = User.objects.create_user(username, email, password)

        user.first_name = first_name
        user.last_name = last_name
        user.save()

        # If the user already has a contact, retrieve it.
        # Otherwise, create a new one.
        contact = None
        if not force_new_contact:
            try:
                contact = Contact.objects.from_request(request, create=False)
            except Contact.DoesNotExist:
                pass

        if contact is None:
            contact = Contact()

        contact.user = user
        contact.first_name = first_name
        contact.last_name = last_name
        contact.email = email
        contact.role = ContactRole.objects.get(pk='Customer')
        contact.title = data.get('title', '')
        contact.save()

        if 'newsletter' not in data:
            subscribed = False
        else:
            subscribed = data['newsletter']

        signals.satchmo_registration.send(self, contact=contact, subscribed=subscribed, data=data)

        if not verify:
            user = authenticate(username=username, password=password)
            login(request, user)
            send_welcome_email(email, first_name, last_name)
            signals.satchmo_registration_verified.send(self, contact=contact)

        self.contact = contact

        return contact

class RegistrationAddressForm(RegistrationForm, ContactInfoForm):
    """Registration form which also requires address information."""

    def __init__(self, *args, **kwargs):
        super(RegistrationAddressForm, self).__init__(*args, **kwargs)

    def save(self, request=None, **kwargs):
        contact = self.save_contact(request)
        kwargs['contact'] = contact

        log.debug('Saving address for %s', contact)
        self.save_info(**kwargs)

        return contact
