"""Calculates the shipping based on the data provided by the zones app
"""
from livesettings import config_value
from django.utils.translation import ugettext_lazy as _
from shipping.modules.base import BaseShipper

from primifrutti.zones.models import Shipments
from primifrutti.utils import HumanizeTimes

time_format = "%H:%M"


class Shipper(BaseShipper):
    id = "Calendar"

    def __str__(self):
        """This is mainly helpful for debugging purposes
        """
        return u"Calendar shipping"

    def description(self):
        """A basic description that will be displayed to the user
        when selecting their shipping options
        """
        return _(u"Calendar shipping")

    def cost(self, order=None): # pylint: disable=W0613
        """Calculates the cost of the shipping
        """
        rate = config_value('SHIPPING', 'SHIPPING_RATE')
        return rate

    def valid(self, order=None): # pylint: disable=W0613
        """Whether or not this shipping method is available
        """
        is_active = config_value('SHIPPING', 'ACTIVE')
        return is_active

    def method(self):
        return 'Corriere privato'

    def expectedDelivery(self, contact=None):
        """Performs calculation on the next available shipping, condiering
        calendars and zones
        """
        if not contact:
            contact = self.contact
        zone = contact.contactzone.zone
        shipments = Shipments(zone)
        e_date, e_mission = shipments.projected_shipment()
        start = e_mission.starts
        end = e_mission.ends
        humanize_times = HumanizeTimes()
        date_str = humanize_times.humanizeTimeDiffLeft(e_date)
        start_str = start.strftime(time_format)
        end_str = end.strftime(time_format)
        remaining_shipments = e_mission.remaining_shipments(e_date)

        rs = _(u'(remaining %(slots)s free slot)') % {
                'slots': remaining_shipments
        }

        if remaining_shipments > 1:
            rs = _(u'(remaining %(slots)s free slots)') % {
                'slots': remaining_shipments
            }

        return u"%(date)s, %(start)s - %(end)s " \
                u"<strong class='%(class)s'>%(rs)s</strong>" % {
            'date': date_str,
            'start': start_str,
            'end': end_str,
            'class': remaining_shipments < 2 and 'cslot bit' or 'cslot',
            'rs': rs
        }
