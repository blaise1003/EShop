from signals_ahoy.signals import form_init
from satchmo_store.contact.forms import ExtendedContactInfoForm, ContactInfoForm


def form_contactinfo_init_handler(sender, form, **kwargs):
    for f in form.fields:
        fld = form.fields[f]
        if fld.required:
            fld.label = fld.label.strip('*')


def form_contactinfo_init_handler_wrapper(sender, **kwargs):
    if (sender == ContactInfoForm) \
        or (sender == ExtendedContactInfoForm):
        form_contactinfo_init_handler(sender, **kwargs)

form_init.connect(form_contactinfo_init_handler_wrapper)
