from django.utils.translation import ugettext_lazy as _
from django.forms import ModelChoiceField
from satchmo_store.contact.models import Contact
from payment.forms import PaymentContactInfoForm, SimplePayShipForm
from satchmoutils.formextender import Extender, ExtraField, Fieldset
from models import Zone, ContactZone, Shipments


class CheckoutZoneExtender(Extender):
    extends = (PaymentContactInfoForm,)

    fieldsets = [
        Fieldset(
            id_='zones',
            label=_(u'Zones informations'),
            fields=('zone',),
            before='shipping',
        )
    ]

    @classmethod
    def get_fields(cls):
        return [
            ExtraField(
                ModelChoiceField,
                name='zone',
                css_class='noclass',
                label=_(u"Zone"),
                required=True,
                queryset=Zone.objects.filter(active=True)
            )
        ]

    @classmethod
    def handle_initdata(cls, **kwargs):
        """ init zone field into checkout form """
        # pylint: disable=W0212
        form = kwargs['form']
        if hasattr(form, '_contact') and isinstance(form._contact, Contact):
            contact = form._contact
            if hasattr(contact, 'contactzone'):
                z_info = contact.contactzone
                if z_info.zone:
                    form.initial['zone'] = z_info.zone.id

    @classmethod
    def handle_postsave(cls, **kwargs):
        """ save zone information into ContactZone object """
        form = kwargs['form']
        data = form.cleaned_data
        contact = form.order.contact
        zone = data['zone']
        if hasattr(contact, 'contactzone'):
            z_info = contact.contactzone
        else:
            z_info = ContactZone(contact=contact)
        zone_obj = Zone.objects.get(id=zone.id)
        z_info.zone = zone_obj
        z_info.save()


class PayShipFormExtender(Extender):

    extends = (SimplePayShipForm,)

    @classmethod
    def handle_postsave(cls, **kwargs):
        """ create shipment for this order """
        form = kwargs['form']
        order = form.order
        contact = order.contact
        zone = contact.contactzone.zone
        shipments = Shipments(zone)
        shipment = shipments.obtain_shipment(order)
        return shipment
