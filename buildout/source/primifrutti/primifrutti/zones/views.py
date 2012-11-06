# -*- coding: utf-8 -*-
from datetime import datetime
from livesettings import config_value
from django.http import HttpResponseRedirect
from django.core import urlresolvers
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.sites import site
from django.utils.safestring import mark_safe
from django.utils.text import capfirst
from django.utils.translation import ugettext as _
from django.utils.formats import date_format, time_format
from django.views.generic.list import ListView

from primifrutti.zones.models import Zone, Shipments, Shipment
from primifrutti.utils import HumanizeTimes


# Utility class for Shipments retrieve and filtring actions
class ShipmentsHandler(object):
    sorting_dict = {
        'contact_name': 'contact',
        'delivery_date': 'delivery_date',
        'booking_date': 'booking_date',
        'order_id': 'order_id',
        '': 'order_id'
    }
    
    def __init__(self, limit=None, contact='', sort_on=''):
        self.limit = limit
        self.max_days = int(config_value('ZONES_INFO', 'MAX_DAYS'))
        self.contact_name = contact.lower()
        self.sort_on = sort_on
        self.get_stale_shipments()

    def get_delivery_date(self, e_date, e_mission):
        return datetime(
            e_date.year,
            e_date.month,
            e_date.day,
            e_mission.starts.hour,
            e_mission.starts.minute)

    def get_ship_date_label(self, e_date, e_mission):
        start = e_mission.starts
        end = e_mission.ends
        date_str = date_format(e_date)
        start_str = time_format(start)
        end_str = time_format(end)
        return "%(date)s, %(start)s - %(end)s" % {
            'date': date_str,
            'start': start_str,
            'end': end_str}

    def order_shipment(self, shipments=[]):
        return sorted(shipments, cmp=lambda x,y: cmp(
            x[self.sorting_dict[self.sort_on]],
            y[self.sorting_dict[self.sort_on]]))

    def get_stale_shipments(self):
        zones = Zone.objects.all()
        risky_count = 0
        stale_shipments = []
        now = datetime.utcnow().date()
        for zone in zones:
            shipments = Shipments(zone)
            for shipment in shipments.stale_shipments(self.max_days):
                # check if this shipment is "risky"
                e_date, e_mission = shipments.projected_shipment()
                diff_days = e_date - now
                if diff_days.days < 3:
                    # risky stale shipment
                    risky_count += 1

                # storing shipment
                humanize_times = HumanizeTimes()
                shipment_vocab = {
                    'id': shipment.id,
                    'order_id': shipment.order.id,
                    'zone': shipment.zone,
                    'booked_on': humanize_times.humanizeTimeDiffAgo(shipment.booked_on),
                    'ship_on': self.get_ship_date_label(e_date, e_mission),
                    'booking_date': shipment.booked_on,
                    'delivery_date': self.get_delivery_date(e_date, e_mission),
                    'contact': shipment.order.contact.full_name,
                    'contact_email': shipment.order.contact.email,
                    'primary_phone': shipment.order.contact.primary_phone}

                if self.contact_name:
                    if self.contact_name in \
                            shipment.order.contact.full_name.lower():
                        stale_shipments.append(shipment_vocab)
                else:
                    stale_shipments.append(shipment_vocab)

        self.total_shipments = len(stale_shipments)
        if self.limit:
            stale_shipments = stale_shipments[:self.limit]
        self.stale_shipments = self.order_shipment(stale_shipments)
        self.risky_count = risky_count


# Stale shipments admin view
def stale_shipments(request):
    shipment_handler = ShipmentsHandler(limit=5)
    stale_shipments = shipment_handler.stale_shipments
    risky_count = shipment_handler.risky_count
    total_shipments = shipment_handler.total_shipments

    app_dict = {}
    user = request.user
    for model, model_admin in site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = user.has_module_perms(app_label)

        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'admin_url': mark_safe('%s/%s/' % (app_label,
                                            model.__name__.lower())),
                    'perms': perms,
                }
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'name': app_label.title(),
                        'app_url': app_label + '/',
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                    }

    # Sort the apps alphabetically.
    app_list = app_dict.values()
    app_list.sort(key=lambda x: x['name'])

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])

    context = {
        'title': _('Site administration'),
        'app_list': app_list,
        'root_path': site.root_path,
        'stale_shipments': stale_shipments,
        'total_shipments': total_shipments,
        'risky_count': risky_count}

    ctx = RequestContext(request, context)

    return render_to_response('zones/admin_views/stale_shipments.html',
        context_instance=ctx)


stale_shipments = user_passes_test(lambda u: u.is_authenticated() and \
    u.is_staff, login_url='/admin/')(stale_shipments)


# deliveries list view
class Deliveries(ListView):
    template_name = "zones/admin_views/deliveries.html"
    context_object_name = "stale_shipments"
    paginate_by = 10

    def get_queryset(self):
        contact_name = self.request.GET.get('contact_name', '')
        order_by = self.request.GET.get('order_by', '')
        shipment_handler = ShipmentsHandler(
            limit=None, contact=contact_name, sort_on=order_by)
        self.stale_shipments = shipment_handler.stale_shipments
        self.risky_count = shipment_handler.risky_count
        return self.stale_shipments

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super(Deliveries, self).get_context_data(**kwargs)
        # Add some values to context
        msg = self.request.GET.get('msg', '')
        context['title'] = _('Stale shipments')
        context['risky_count'] = self.risky_count
        context['msg'] = msg
        return context


deliveries = Deliveries.as_view()


# confirm shipment utility view
def confirm_shipment(request, id=None):
    if id:
        try:
            shipment = Shipment.objects.get(id=id)
            shipment.confirmed = True
            shipment.save()
            msg = _(u"Shipment %(id)s confirmed" % {'id': id})
        except Shipment.DoesNotExist:
            msg = _(u"Error! Shipment %(id)s doeasn't exist" % {'id': id})
    else:
        msg = _(u"No sipment selected")

    url = "%s?msg=%s" % (urlresolvers.reverse('satchmo_deliveries'), msg)
    return HttpResponseRedirect(url)


confirm_shipment = user_passes_test(lambda u: u.is_authenticated() and \
    u.is_staff,
    login_url='/admin/')(confirm_shipment)
