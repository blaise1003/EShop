# -*- coding: utf-8 -*-
from livesettings import config_value
from django.utils.translation import ugettext_lazy as _
from satchmo_store.contact.models import Contact

from .models import Invite, InviterDiscount


# Utility class for Invites
class InvitesUtils(object):
    sorting_dict = {
        'contact_name': 'contact',
        'contact_id': 'contact_id',
        '': 'contact_id'}

    def __init__(self, limit=None, contact='', sort_on=''):
        self.limit = limit
        self.max_invites = int(config_value('INVITES_SETTINGS', 'MAX_INVITES'))
        self.contact_name = contact.lower()
        self.sort_on = sort_on
        self.get_contacts_invites()

    def order_contacts_invites(self, shipments=[]):
        return sorted(shipments, cmp=lambda x, y: cmp(
            x[self.sorting_dict[self.sort_on]],
            y[self.sorting_dict[self.sort_on]]))

    def get_last_coupon(self, user):
        inviter_discount = InviterDiscount.objects.filter(
            user=user).order_by('-pk')
        if inviter_discount.count():
            inviter_discount = inviter_discount[0]
            return inviter_discount.coupon
        return None

    def get_contact_map(self, contact):
        coupon = self.get_last_coupon(contact.user)
        not_used_invites = Invite.objects.get_for_user(
            contact.user, used=False).count()
        used_invites = Invite.objects.get_for_user(
            contact.user, used=True).count()
        invites_sended = not_used_invites + used_invites
        invited_people = Invite.objects.get_invited_by(
            inviter=contact.user, used=True)
        if contact.user:
            contact_user_id = contact.user.id
        else:
            contact_user_id = None
        return {
            'contact_id': contact.id,
            'user_id': contact.user and contact_user_id or contact.id,
            'contact': contact.full_name,
            'invites_sended': _(u"%(invites_sended)i/%(max_invites)i") % {
                'invites_sended': invites_sended,
                'max_invites': self.max_invites},
            'not_used_invites': _(u"%(not_used_invites)i") % {
                'not_used_invites': not_used_invites,},
            'used_invites': _(u"%(used_invites)i") % {
                'used_invites': used_invites,},
            'invited_people': invited_people,
            'num_invited_people': len(invited_people),
            'coupon': coupon,
            'contact_email': contact.email}

    def get_contacts_invites(self):
        contacts = Contact.objects.all()
        contacts_invites = []
        for contact in contacts:
            contact_invites_vocab = self.get_contact_map(contact)
            if self.contact_name:
                if self.contact_name in contact.full_name.lower():
                    contacts_invites.append(contact_invites_vocab)
            else:
                contacts_invites.append(contact_invites_vocab)
        self.contacts_invites = self.order_contacts_invites(contacts_invites)
