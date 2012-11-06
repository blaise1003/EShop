from django import forms
from django.utils.translation import ugettext_lazy as _
from captcha.fields import CaptchaField


class InviteForm(forms.Form):
    recipient = forms.EmailField(_(u'email address'),
        required=True,
        help_text=_(u"Email address of your friend"))
    recipient_name = forms.CharField(_(u'first name'),
        required=True,
        help_text=_(u"Your friend's name"))
    recipient_surname = forms.CharField(_(u'last name'),
        required=True,
        help_text=_(u"Your friend's surname"))
    text = forms.CharField(_(u'personal note'),
        widget=forms.Textarea({'cols': '30', 'rows': '3'}),
        required=False,
        help_text=_(u"Send a personal message to invite your friend"))
    captcha = CaptchaField(required=True,
        help_text=_(u"Insert following word"))
