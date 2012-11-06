"""
Stores customer, organization, and order information.
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _
from l10n.models import Country
from satchmo_store.contact import CUSTOMER_ID
import datetime
import logging

log = logging.getLogger('contact.models')

class ContactRole(models.Model):
    key = models.CharField(_('Key'), max_length=30, unique=True, primary_key=True)
    name = models.CharField(_('Name'), max_length=40)

    def __unicode__(self):
        return ugettext(self.name)


class ContactOrganization(models.Model):
    key = models.CharField(_('Key'), max_length=30, unique=True, primary_key=True)
    name = models.CharField(_('Name'), max_length=40)

    def __unicode__(self):
        return ugettext(self.name)

    class Meta:
        verbose_name = _('Contact organization type')


class ContactOrganizationRole(models.Model):
    key = models.CharField(_('Key'), max_length=30, unique=True, primary_key=True)
    name = models.CharField(_('Name'), max_length=40)

    def __unicode__(self):
        return ugettext(self.name)

class ContactInteractionType(models.Model):
    key = models.CharField(_('Key'), max_length=30, unique=True, primary_key=True)
    name = models.CharField(_('Name'), max_length=40)

    def __unicode__(self):
        return ugettext(self.name)


class OrganizationManager(models.Manager):
    def by_name(self, name, create=False, role='Customer', orgtype='Company'):
        org = None
        orgs = self.filter(name=name, role__key=role, type__key=orgtype)
        if orgs.count() > 0:
            org = orgs[0]

        if not org:
            if not create:
                raise Organization.DoesNotExist()
            else:
                log.debug('Creating organization: %s', name)
                role = ContactOrganizationRole.objects.get(pk=role)
                orgtype = ContactOrganization.objects.get(pk=orgtype)
                org = Organization(name=name, role=role, type=orgtype)
                org.save()

        return org

class Organization(models.Model):
    """
    An organization can be a company, government or any kind of group.
    """
    name = models.CharField(_("Name"), max_length=50, )
    type = models.ForeignKey(ContactOrganization, verbose_name=_("Type"), null=True)
    role = models.ForeignKey(ContactOrganizationRole, verbose_name=_("Role"), null=True)
    create_date = models.DateField(_("Creation Date"))
    notes = models.TextField(_("Notes"), max_length=200, blank=True, null=True)

    objects = OrganizationManager()

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        super(Organization, self).save(**kwargs)

    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

class ContactManager(models.Manager):

    def from_request(self, request, create=False):
        """Get the contact from the session, else look up using the logged-in
        user. Create an unsaved new contact if `create` is true.

        Returns:
        - Contact object or None
        """

        contact = None
        if request.user.is_authenticated():
            try:
                contact = Contact.objects.get(user=request.user.id)
                request.session[CUSTOMER_ID] = contact.id
            except Contact.DoesNotExist:
                pass
        else:
            # Don't create a Contact if the user isn't authenticated.
            create = False
            
        if request.session.get(CUSTOMER_ID):
            try:
                contactBySession = Contact.objects.get(id=request.session[CUSTOMER_ID])
                if contact is None:
                    contact = contactBySession
                elif contact != contactBySession:
                    # For some reason the authenticated id and the session customer ID don't match.
                    # Let's bias the authenticated ID and kill this customer ID:
                    log.debug("CURIOUS: The user authenticated as %r (contact id:%r) and a session as %r (contact id:%r)" %
                               (contact.user.get_full_name(), contact.id, Contact.objects.get(id=request.session[CUSTOMER_ID]).full_name, request.session[CUSTOMER_ID]))
                    log.debug("Deleting the session contact.")
                    del request.session[CUSTOMER_ID]
            except Contact.DoesNotExist:
                log.debug("This user has a session stored customer id (%r) which doesn't exist anymore. Removing it from the session." % request.session[CUSTOMER_ID])
                del request.session[CUSTOMER_ID]

        if contact is None:
            if create:
                contact = Contact(user=request.user)

            else:
                raise Contact.DoesNotExist()

        return contact


class Contact(models.Model):
    """
    A customer, supplier or any individual that a store owner might interact
    with.
    """
    title = models.CharField(_("Title"), max_length=30, blank=True, null=True)
    first_name = models.CharField(_("First name"), max_length=30, )
    last_name = models.CharField(_("Last name"), max_length=30, )
    user = models.ForeignKey(User, blank=True, null=True, unique=True)
    role = models.ForeignKey(ContactRole, verbose_name=_("Role"), null=True)
    organization = models.ForeignKey(Organization, verbose_name=_("Organization"), blank=True, null=True)
    dob = models.DateField(_("Date of birth"), blank=True, null=True)
    email = models.EmailField(_("Email"), blank=True, max_length=75)
    notes = models.TextField(_("Notes"), max_length=500, blank=True)
    create_date = models.DateField(_("Creation date"))

    objects = ContactManager()

    def _get_full_name(self):
        """Return the person's full name."""
        return u'%s %s' % (self.first_name, self.last_name)
    full_name = property(_get_full_name)

    def _shipping_address(self):
        """Return the default shipping address or None."""
        try:
            return self.addressbook_set.get(is_default_shipping=True)
        except AddressBook.DoesNotExist:
            return None
    shipping_address = property(_shipping_address)

    def _billing_address(self):
        """Return the default billing address or None."""
        try:
            return self.addressbook_set.get(is_default_billing=True)
        except AddressBook.DoesNotExist:
            return None
    billing_address = property(_billing_address)

    def _primary_phone(self):
        """Return the default phone number or None."""
        try:
            return self.phonenumber_set.get(primary=True)
        except PhoneNumber.DoesNotExist:
            return None
    primary_phone = property(_primary_phone)

    def __unicode__(self):
        return self.full_name

    def save(self, **kwargs):
        """Ensure we have a create_date before saving the first time."""
        if not self.pk:
            self.create_date = datetime.date.today()
        # Validate contact to user sync
        if self.user:
            dirty = False
            user = self.user
            if user.email != self.email:
                user.email = self.email
                dirty = True

            if user.first_name != self.first_name:
                user.first_name = self.first_name
                dirty = True

            if user.last_name != self.last_name:
                user.last_name = self.last_name
                dirty = True

            if dirty:
                self.user = user
                self.user.save()

        super(Contact, self).save(**kwargs)

    def _get_address_book_entries(self):
        """ Return all non primary shipping and billing addresses
        """
        return AddressBook.objects.filter(contact=self.pk).exclude(is_default_shipping=True).exclude(is_default_billing=True)
        
    address_book_entries=property(_get_address_book_entries)
        
    class Meta:
        verbose_name = _("Contact")
        verbose_name_plural = _("Contacts")

PHONE_CHOICES = (
    ('Work', _('Work')),
    ('Home', _('Home')),
    ('Fax', _('Fax')),
    ('Mobile', _('Mobile')),
)

class Interaction(models.Model):
    """
    A type of activity with the customer.  Useful to track emails, phone calls,
    or in-person interactions.
    """
    contact = models.ForeignKey(Contact, verbose_name=_("Contact"))
    type = models.ForeignKey(ContactInteractionType, verbose_name=_("Type"))
    date_time = models.DateTimeField(_("Date and Time"), )
    description = models.TextField(_("Description"), max_length=200)

    def __unicode__(self):
        return u'%s - %s' % (self.contact.full_name, self.type)

    class Meta:
        verbose_name = _("Interaction")
        verbose_name_plural = _("Interactions")

class PhoneNumber(models.Model):
    """
    Phone number associated with a contact.
    """
    contact = models.ForeignKey(Contact)
    type = models.CharField(_("Description"), choices=PHONE_CHOICES,
        max_length=20, blank=True)
    phone = models.CharField(_("Phone Number"), blank=True, max_length=30,
        )
    primary = models.BooleanField(_("Primary"), default=False)

    def __unicode__(self):
        return u'%s - %s' % (self.type, self.phone)

    def save(self, **kwargs):
        """
        If this number is the default, then make sure that it is the only
        primary phone number. If there is no existing default, then make
        this number the default.
        """
        existing_number = self.contact.primary_phone
        if existing_number:
            if self.primary:
                existing_number.primary = False
                super(PhoneNumber, existing_number).save()
        else:
            self.primary = True
        super(PhoneNumber, self).save(**kwargs)

    class Meta:
        ordering = ['-primary']
        verbose_name = _("Phone Number")
        verbose_name_plural = _("Phone Numbers")

class AddressBook(models.Model):
    """
    Address information associated with a contact.
    """
    contact = models.ForeignKey(Contact)
    description = models.CharField(_("Description"), max_length=20, blank=True,
        help_text=_('Description of address - Home, Office, Warehouse, etc.',))
    addressee = models.CharField(_("Addressee"), max_length=80)
    street1 = models.CharField(_("Street"), max_length=80)
    street2 = models.CharField(_("Street"), max_length=80, blank=True)
    state = models.CharField(_("State"), max_length=50, blank=True)
    city = models.CharField(_("City"), max_length=50)
    postal_code = models.CharField(_("Zip Code"), max_length=30)
    country = models.ForeignKey(Country, verbose_name=_("Country"))
    is_default_shipping = models.BooleanField(_("Default Shipping Address"),
        default=False)
    is_default_billing = models.BooleanField(_("Default Billing Address"),
        default=False)

    def __unicode__(self):
       return u'%s - %s' % (self.contact.full_name, self.description)

    def save(self, **kwargs):
        """
        If this address is the default billing or shipping address, then
        remove the old address's default status. If there is no existing
        default, then make this address the default.
        """
        existing_billing = self.contact.billing_address
        if existing_billing:
            if self.is_default_billing:
                existing_billing.is_default_billing = False
                super(AddressBook, existing_billing).save()
        else:
            self.is_default_billing = True

        existing_shipping = self.contact.shipping_address
        if existing_shipping:
            if self.is_default_shipping:
                existing_shipping.is_default_shipping = False
                super(AddressBook, existing_shipping).save()
        else:
            self.is_default_shipping = True

        super(AddressBook, self).save(**kwargs)

    class Meta:
        verbose_name = _("Address Book")
        verbose_name_plural = _("Address Books")

import config
