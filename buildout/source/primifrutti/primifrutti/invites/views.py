# -*- coding: utf-8 -*-
from logging import getLogger
from livesettings import config_get_group, config_value
from django.core import urlresolvers
from django.contrib.auth.decorators import user_passes_test, login_required
from django.views.decorators.csrf import requires_csrf_token
from django.template import RequestContext, loader
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.contrib.auth.models import User
from django.views.generic.list import ListView

from satchmo_store.accounts.views import register_handle_form

from .models import Invite
from .form import InviteForm
from .utils import InvitesUtils


@requires_csrf_token
def invalid_code(request, invite_code='', template_name='invites/404.html'):
    """ Custom 404 handler for invalid invite code. """
    template = loader.get_template(template_name)
    return HttpResponseNotFound(template.render(
        RequestContext(request, {
            'request_path': request.path,
            'message': _(u"Invite code already used : %(invite_code)s" % {
                'invite_code': invite_code,
            })})))


def register_from_invite(request, redirect=None, invite_code=''):
    """ Wrapping registration form view for insert 'next' url paramenter
    """
    # XXX: I copied the code of the register of Satchmo because in this
    # moment I have not found a better way to pass the
    # parameter 'next' to the template

    # Check if invite_code is still valid
    try:
        invite = Invite.objects.get_by_code(code=invite_code)
    except Invite.DoesNotExist:
        return invalid_code(request, invite_code)

    template = 'invites/registration_form.html'
    ret = register_handle_form(request, redirect)
    success = ret[0]
    todo = ret[1]
    if len(ret) > 2:
        extra_context = ret[2]
    else:
        extra_context = {}

    if success:
        return todo
    else:
        if config_get_group('NEWSLETTER'):
            show_newsletter = True
        else:
            show_newsletter = False

        ctx = {
            'form': todo,
            'recipient': invite.recipient,
            'title': _(u'Registration Form'),
            'show_newsletter': show_newsletter,
            'allow_nickname': config_value('SHOP', 'ALLOW_NICKNAME_USERNAME'),
            'next': reverse('invites_confirm', args=[invite_code])}

        if extra_context:
            ctx.update(extra_context)

        context = RequestContext(request, ctx)
        return render_to_response(template, context_instance=context)


def confirm(request, invite_code): # pylint: disable=W0613
    """ Confirm registration after invitation
    """
    try:
        invite = Invite.objects.get_by_code(invite_code)
    except Invite.DoesNotExist:
        logger = getLogger('primifrutti.invites')
        logger.warning(
            "Registration with a nonexistant invite code '%s'" % invite_code)
        logger.info("Skipping invite processing for '%s'" % invite_code)
    else:
        invite.used = True
        user = User.objects.get(email=invite.recipient)
        invite.invited = user
        invite.save()
    return HttpResponseRedirect(reverse('registration_complete'))


# Invites Form View
def get_invite_form(request):
    return_message = ''
    if request.method == 'POST':
        form = InviteForm(request.POST)
        if form.is_valid():
            return_message = invites_action(form)
        else:
            return_message = {'message_type': 'error',
               'message_text': _(u"Error! Check your input")}
    else:
        form = InviteForm()
    return form, return_message


@login_required(login_url='/accounts/login/')
def invite(request):
    """Invites form view"""
    user = request.user
    max_invites = int(config_value('INVITES_SETTINGS', 'MAX_INVITES'))
    invites = Invite.objects.get_for_user(user, countable=True).count()
    invites_available = invites < max_invites

    if not invites_available:
        raise Invite.OverQuota(user)

    form, return_message = get_invite_form(request)

    context = RequestContext(request, {
        'form': form,
        'message': return_message})
    return render_to_response(
        "invites/invites_form.html",
        context_instance=context)


def invites_action(form):
    """Execute the invite user action.

    Sends an email to the email address taken from request.
    """
    recipient = form.cleaned_data['recipient']
    recipient_name = form.cleaned_data['recipient_name']
    recipient_surname = form.cleaned_data['recipient_surname']
    text = form.cleaned_data['text']

    try:
        user = User.objects.get(username=form.data['user'])
    except User.DoesNotExist:
        msg = {'message_type': 'error',
               'message_text': _(u"Error! Check your input")}
        return msg
    
    invites = Invite.objects.filter(
        inviter=user,
        recipient=recipient,
    )
    if invites:
        msg = {'message_type': 'error',
               'message_text': _(u"Error! You have already invited this friend")}
    else:
        Invite.objects.create(
            user=user,
            recipient=recipient,
            recipient_name=recipient_name,
            recipient_surname=recipient_surname,
            text=text)
        msg = {'message_type': 'success',
               'message_text': _(u"Invite created!")}

    return msg


# Invites report admin view
class AdminInvitesBase(ListView):
    """ Base View for Invites Admin
    """
    context_object_name = "contacts_invites"
    paginate_by = 10

    def get_queryset(self):
        contact_name = self.request.GET.get('contact_name', '')
        order_by = self.request.GET.get('order_by', '')
        invites_handler = InvitesUtils(
            limit=None, contact=contact_name, sort_on=order_by)
        self.contacts_invites = invites_handler.contacts_invites
        return self.contacts_invites

    def get_context_data(self, **kwargs):
        context = super(AdminInvitesBase, self).get_context_data(**kwargs)
        msg = self.request.GET.get('msg', '')
        context['title'] = _('Invites Report')
        context['max_invites'] = InvitesUtils().max_invites
        context['msg'] = msg
        return context


class ContactsInvites(AdminInvitesBase):
    """ Admin View to manage contacts and invites.
    For each contact:
    1. shows available invites;
    2. shows used/unused invites;
    3. permits to send email to the contact;
    4. permits to reset available contact's invites.
    """
    template_name = "invites/admin_views/invites_report.html"


invites_report = ContactsInvites.as_view()


class InvitesRelationships(AdminInvitesBase):
    """ Admin Report View that shows contacts invited relationships
    """
    template_name = "invites/admin_views/invites_report_relationships.html"


invites_relationships = InvitesRelationships.as_view()


# reset invites for given user (by ID)
def invites_reset(request, user_id=None):
    """ This view reset available invites for given contact (by contact id)
    """
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            Invite.objects.reset_for_user(user, site=None)
            msg = _(u"Invites for user %(id)s resetted" % {'id': user_id})
        except User.DoesNotExist:
            msg = _(u"Error! User %(id)s doesn't exist" % {'id': user_id})
    else:
        msg = _(u"No user selected")

    url = "%s?msg=%s" % (urlresolvers.reverse('satchmo_invites_report'), msg)
    return HttpResponseRedirect(url)


invites_reset = user_passes_test(lambda u: u.is_authenticated() and \
    u.is_staff,
    login_url='/admin/')(invites_reset)
