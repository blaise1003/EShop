from django.contrib.sites.models import RequestSite
from django.contrib.sites.models import Site
from django.conf import settings

from registration import signals
from satchmo_store.accounts.forms import RegistrationForm
from satchmo_utils.unique_id import generate_id
from satchmo_store.contact.models import Contact, ContactRole

from primifrutti.shop.models import HtmlRegistrationProfile


class HtmlBackend(object):
    """Override Default Backend in order to send htnl format activation email
    """

    def register(self, request, **kwargs):
        """Use HtmlRegistrationProfile instead of default RegistrationProfile
        """
        username = kwargs['username']
        email = kwargs['email']
        password = kwargs['password1']
        first_name = kwargs['first_name']
        last_name = kwargs['last_name']
        if not username:
            username = generate_id(first_name, last_name, email)
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = HtmlRegistrationProfile.objects.create_inactive_user(
            username, email, password, site)
            
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.save()

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)

        # If the user already has a contact, retrieve it.
        # Otherwise, create a new one.
        contact = None
        try:
            contact = Contact.objects.from_request(request, create=False)
        except Contact.DoesNotExist:
            pass

        if contact is None:
            contact = Contact()

        contact.user = new_user
        contact.first_name = first_name
        contact.last_name = last_name
        contact.email = email
        contact.role = ContactRole.objects.get(pk='Customer')
        contact.title = "%s %s" % (first_name, last_name)
        contact.save()
        
        return new_user

    def activate(self, request, activation_key):
        """
        """
        activated = HtmlRegistrationProfile.objects.activate_user(activation_key)
        if activated:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated,
                                        request=request)
        return activated

    def registration_allowed(self, request):
        return getattr(settings, 'REGISTRATION_OPEN', True)

    def get_form_class(self, request):
        return RegistrationForm

    def post_registration_redirect(self, request, user):
        next = request.POST.get('next', None)
        if next:
            next = next.rstrip('/')
            return ('invites_confirm', (), {'invite_code': next.split('/')[-1]})
        return ('registration_complete', (), {})

    def post_activation_redirect(self, request, user):
        return ('registration_activation_complete', (), {})
