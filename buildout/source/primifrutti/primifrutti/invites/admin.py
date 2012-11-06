from django.utils.translation import ugettext_lazy as _
from django.contrib import admin

from models import InviteDiscount

import config # pylint: disable=W0611


class InviteDiscountOptions(admin.ModelAdmin):

    __name__ = _(u"InviteDiscount Options")

    list_display = ('site', 'invites_target', 'amount', 'percentage')
    list_display_links = ('invites_target',)


admin.site.register(InviteDiscount, InviteDiscountOptions)
