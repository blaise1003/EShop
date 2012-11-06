# -*- coding: utf-8 -*-
from logging import getLogger
from datetime import datetime, timedelta
from django.db.models.signals import post_save, post_delete
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import (Model, ForeignKey, CharField, IntegerField,
                              BooleanField, TimeField, DateField,
                              OneToOneField, DateTimeField, Q)
from django.utils.translation import ugettext_lazy as _
from django.utils.formats import date_format, time_format
from django.contrib.sites.models import Site

from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Order, OrderStatus

import config


class ContactZone(Model):
    contact = OneToOneField(
        Contact,
        verbose_name = _("contact")
    )
    zone = ForeignKey(
        'Zone',
        verbose_name = _("zone")
    )

    def __unicode__(self):
        return _(u"zone for %(contact_name)s") % {
            'contact_name': self.contact.full_name
        }

    class Meta:
        verbose_name = _("zone for contact")
        verbose_name_plural = _("zones of contacts")


def overlapping_query(instance, from_field, to_field, primary_key='id'):
    """Returns a query that should return all the overlapping time slices.

    In a model that defines a time slice (generally with a field *from* and a
    field *to*) is often necessary to determine if there are any overlapping
    slices. This function returns the query that will yield all the slices
    conflicting with the one passed as ``instance``.

    ``from_field`` and ``to_field`` are the names of the fields determining the
    slice, as strings, while ``instance`` should be the reference point
    (instance of the model).

    The ``primary_key`` parameter is the name of the primary key field, and
    defaults to ``id``.

    It returns a ``django.db.models.Q`` object.
    """
    from_ = getattr(instance, from_field)
    to = getattr(instance, to_field)
    pkey = getattr(instance, primary_key, None)
    left = Q(**{'%s__range' % from_field: (from_, to)})
    right = Q(**{'%s__range' % to_field: (from_, to)})
    inset = Q(**{'%s__gte' % from_field: from_,
                 '%s__lte' % to_field: to})
    outset = Q(**{'%s__lte' % from_field: from_,
                  '%s__gte' % to_field: to})
    if pkey:
        itself = Q(**{'%s__exact' % primary_key: pkey})
        return (left | right | inset | outset) & ~itself
    else:
        return left | right | inset | outset


class Zone(Model):
    """A delivery zone.

    The city is divided into multiple zones, and delivery scheduling takes the
    zone as the atomic delivery destination used for semantical grouping of
    deliveries.
    """

    site = ForeignKey(Site, verbose_name=_(u"site"))
    name = CharField(_(u"zone name"), max_length=256)
    active = BooleanField(_(u"active"), default=False)

    def default_calendar(self):
        try:
            return self.calendar_set.get(
                valid_from__isnull=True,
                valid_to__isnull=True
            )
        except Calendar.DoesNotExist:
            pass
        return None

    def check_validity(self):
        """Checks the "validity" of the zone.

        For a zone, being valid means that:
         * The default calendar exists
         * The default calendar has (at least) one day associated with it and
           that this contains (at least) one mission

        Should one of the two fail, ``ValidationError`` is raised.
        """
        default_calendar = self.default_calendar()
        # Check that we have a default calendar
        if default_calendar is None:
            raise ValidationError(
                _(u"%(zone)s doesn't have a default calendar associated, "
                  u"please add it") % { 'zone': self.name }
            )
        # Checks that we have atleast one mission associated with one of the
        # days
        missions = Mission.objects.all().filter(
            calendar_day__calendar=default_calendar
        ).count()
        if not (missions > 0):
            raise ValidationError(
                _(u"%(zone)s's default calendar is void, please add at least "
                  u"one mission to it") % { 'zone': self.name }
            )

    def validate(self):
        """If the zone is active, checks that it is still valid.

        Uses ``check_validity`` to check that the zone is still valid: if it
        isn't, the ``active`` property is set to false and the zone is saved.

        Returns the state of ``active`` after the check
        """
        if not self.active:
            return self.active
        try:
            self.check_validity()
        except ValidationError:
            self.active = False
            self.save()
        return self.active

    def activate(self):
        """Activates the zone.

        It uses ``check_validity`` beforehand to check is activation is indeed
        possible.
        """
        self.check_validity()
        self.active = True
        self.save()

    def deactivate(self):
        self.active = False
        self.save()

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name = _("zone")
        verbose_name_plural = _("zones")
        ordering = ['name']


class Calendar(Model):
    """A delivery calendar.

    A calendar is attached to one and only one zone. There are two types of
    calendars: default and exceptions. The default calendar (only one default
    calendar per zone might exist) does not specify a validity period, while
    exceptions do define validity period (which must be non overlapping for
    every single zone, i.e. a zone can't have two overlapping exceptions both
    valid at the same time).

    The exceptions, when they are valid, take precedence over the default
    calendar.

    The calendar also defines *slack days*, meaning that a shipping cannot be
    booked to a time that is before the time of the booking plus the slack
    days: e.g. if ``slack_days`` is equal to two I can't book a delivery today
    for tomorrow but I shall book a later one.
    """

    zone = ForeignKey(Zone, verbose_name=_(u"delivery zone"))
    valid_from = DateField(
        _(u"valid from"),
        blank=True,
        null=True,
        default=None
    )
    valid_to = DateField(
        _(u"valid to"),
        blank=True,
        null=True,
        default=None
    )
    slack_days = IntegerField(_(u"slack days"),
                              validators=[MinValueValidator(0)])

    def clean(self):
        # Checks that either ends of the validity period are specified or none
        # (default calendar)
        if (self.valid_from is None and self.valid_to is not None) or \
                (self.valid_from is not None and self.valid_to is None):
            raise ValidationError(
                _(u"You must specify both ends of the validity period or "
                  u"none at all")
            )
        # If this is a default calendar (no validity period) checks that it is
        # the only one
        if self.valid_from is None:
            filter_ = Q(
                zone=self.zone,
                valid_from__isnull=True,
                valid_to__isnull=True
            )
            if self.pk is not None:
                filter_ &= ~Q(pk=self.pk)
            other_default = self.__class__.objects.all().filter(
                filter_
            ).count()
            if other_default > 0:
                raise ValidationError(
                    _(u"You can specify only one default calendar (with no "
                      u"validity period) per zone")
                )
        else:
            # Checks that the validity period makes sense
            if self.valid_from > self.valid_to:
                raise ValidationError(
                    _(u"The validity period starts after it ends")
                )
            filter_ = Q(zone=self.zone)
            filter_ &= overlapping_query(self, 'valid_from', 'valid_to')
            if self.pk is not None:
                filter_ &= ~Q(pk=self.pk)
            # Checks that there aren't any overlapping definitions
            overlapping = self.__class__.objects.all().filter(
                filter_
            ).count()
            if overlapping > 0:
                raise ValidationError(
                    _(u"There is another calendar present in the validity "
                      u"time of the current one")
                )

    def __unicode__(self):
        template = _(u"%(zone)s's calendar (%(from)s - %(to)s)")
        data = {
            'zone': unicode(self.zone)
        }
        if self.valid_from is None and self.valid_to is None:
            template = _(u"%(zone)s's default calendar")
        else:
            data['from'] = date_format(self.valid_from)
            data['to'] = date_format(self.valid_to)
        return template % data

    class Meta:
        verbose_name = _("calendar")
        verbose_name_plural = _("calendars")
        ordering = ['-valid_from']


# compatible with isoweekday()
WEEK_DAYS = (
    (1, _(u"monday")),
    (2, _(u"tuesday")),
    (3, _(u"wednesday")),
    (4, _(u"thursday")),
    (5, _(u"friday")),
    (6, _(u"saturday")),
    (7, _(u"sunday"))
)


class CalendarDay(Model):
    """A day in the calendar.

    A calendar might not span over all the week days, therefore you must attach
    a day to the calendar (say, "Tuesday") before being able to attach multiple
    "missions" to it.
    """

    calendar = ForeignKey(Calendar, verbose_name=_(u"calendar"))
    weekday = IntegerField(_(u"week day"), choices=WEEK_DAYS)

    def __unicode__(self):
        return _(u"%(weekday)s in %(calendar)s") % {
            'weekday': dict(WEEK_DAYS)[self.weekday],
            'calendar': unicode(self.calendar)
        }

    class Meta:
        unique_together = ('calendar', 'weekday')
        verbose_name = _("calendar day")
        verbose_name_plural = _("calendar days")
        ordering = ['weekday']


class Mission(Model):
    """A delivery mission.

    A delivery mission starts at a given time, on a given day, and visits the
    zone it is attached via calendar. It phisically corresponds to the delivery
    truck arriving in the zone the given day (e.g. "Tuesday") and staying there
    from ``starts`` to ``ends`` (e.g. from 08:00 to 12:00) to make the
    deliveries.

    All the associated shipments addresses will be visited in that timespan,
    according to the most comfortable route for the driver (there is no
    specific delivery hour but it can be anything between the given time
    period.

    It also defines a maximum number of shipments for the mission (e.g. the
    number of actual deliveries the driver can perform in the allowed
    time). This is later used in scheduling.
    """

    calendar_day = ForeignKey(CalendarDay, verbose_name=_(u"calendar day"))
    starts = TimeField(_(u"starts at"))
    ends = TimeField(_(u"ends at"))
    shipments = IntegerField(_(u"maximum shipments"),
                             validators=[MinValueValidator(0)])

    def clean(self):
        # Checks the delivery period makes sense
        if self.starts > self.ends:
            raise ValidationError(_(u"The mission starts after it ends"))
        # We cannot have overlapping missions: there is no concept of
        # concurrent deliveries by multiple trucks
        filter_ = Q(calendar_day=self.calendar_day)
        filter_ &= overlapping_query(self, 'starts', 'ends')
        if self.pk is not None:
            filter_ &= ~Q(pk=self.pk)
        overlapping = self.__class__.objects.all().filter(
            filter_
        ).count()
        if overlapping > 0:
            raise ValidationError(
                _(u"There is another mission to the same zone with a "
                  u"conflicting schedule")
            )

    def remaining_shipments(self, date):
        """Returns the remaining shipments for a given day.

        Calculates how many "free delivery slots" there are for a given mission
        on a given day (e.g. "Tue Dec 20th, 2011"), by looking at the booked
        shipments for that day and subtracting those from the maximum number of
        possible shipments for that mission
        """
        shippings_that_day = Shipment.objects.all().filter(
            mission=self,
            date=date
        ).count()
        return self.shipments - shippings_that_day

    def __unicode__(self):
        return _(u"%(start)s - %(end)s, %(day)s") % {
            'day': unicode(self.calendar_day),
            'start': time_format(self.starts),
            'end': time_format(self.ends)
        }

    class Meta:
        verbose_name = _("mission")
        verbose_name_plural = _("missions")
        ordering = ['starts']


class Shipment(Model):
    """A shipment.

    Contains information about the order it is associated to, when the shipment
    was "booked", and the mission that is supposed to deliver it, and the exact
    date.

    It is important to note that the mission defines something such as
    "Tuesdays between 08:00 and 10:00" while the date actually specifies
    something like "Tue Dec 20th, 2011".

    The shipment also holds a boolean value that needs to be set once the order
    is confirmed, paid and ready for shipping: this allows to periodically
    "clean up" the unfinished or abandoned orders, freeing up precious
    shipments on missions.
    """

    mission = ForeignKey(Mission, verbose_name=_(u"mission"))
    order = ForeignKey(Order, verbose_name=_(u"order"), unique=True)
    date = DateField(_(u"date"))
    booked_on = DateTimeField(_(u"booken on"), editable=False,
                              default=datetime.utcnow)
    confirmed = BooleanField(_(u"confirmed"), default=False)

    @property
    def zone(self):
        zone = self.mission.calendar_day.calendar.zone
        return zone

    def __unicode__(self):
        return _(u"shipment #%(id)s for order #%(order)s") % {
            'id': self.pk,
            'order' : self.order.pk
        }

    class Meta:
        verbose_name = _("shipment")
        verbose_name_plural = _("shipments")


def get_date(from_, weekday, week):
    """Returns the actual date from an information composed of a starting
    point, a week day, and a week span time.

    Substantially, it responds to the question: which date is the week day
    ``weekday``, located ``week`` weeks away from the week the date ``from_``
    sits in?

    When ``week`` is 0 it is considered to be the current week, which gives
    rise to this peculiar behavior::

        >>> from datetime import date
        >>> get_date(date(2011, 12, 16), 1, 0)
        datetime.date(2011, 12, 12)

    Which is **before** from. This is wanted: what I am in fact asking is "give
    me the monday of the week that the 16th of December is in".

    Otherwise, it generally behaves like one expects. Let's see the week the
    16th of December belongs to::

        >>> for day in xrange(1, 8): # isoweekday-like: monday is one
        ...     print get_date(date(2011, 12, 16), day, 0).strftime(
        ...             '%a %b %d, %Y')
        Mon Dec 12, 2011
        Tue Dec 13, 2011
        Wed Dec 14, 2011
        Thu Dec 15, 2011
        Fri Dec 16, 2011
        Sat Dec 17, 2011
        Sun Dec 18, 2011

    And the week after that::

        >>> for day in xrange(1, 8): # isoweekday-like: monday is one
        ...     print get_date(date(2011, 12, 16), day, 1).strftime(
        ...             '%a %b %d, %Y')
        Mon Dec 19, 2011
        Tue Dec 20, 2011
        Wed Dec 21, 2011
        Thu Dec 22, 2011
        Fri Dec 23, 2011
        Sat Dec 24, 2011
        Sun Dec 25, 2011

    And two week after that::

        >>> for day in xrange(1, 8): # isoweekday-like: monday is one
        ...     print get_date(date(2011, 12, 16), day, 2).strftime(
        ...             '%a %b %d, %Y')
        Mon Dec 26, 2011
        Tue Dec 27, 2011
        Wed Dec 28, 2011
        Thu Dec 29, 2011
        Fri Dec 30, 2011
        Sat Dec 31, 2011
        Sun Jan 01, 2012

    .. warning::
       READ ALL OF THE ABOVE CAREFULLY AND DO NOT "FIX" THIS FUNCTION
    """
    return from_ + timedelta(days=(weekday-from_.isoweekday())+(7*week))


class CalendarSchedule(object):
    """An objects that, stating from the "rules" defined in a calendar (and all
    the related "subobjects") is able to tell when the next shipment will take
    place according to that calendar.

    It is mostly used internally. The optional ``missions_queryset`` parameter
    is used when you already have a queryset that returns the missions for the
    given calendar in the proper order and you do not want to re-evaluate
    it. If ``None``, it will be computed, but the queryset will be re-evaluated
    instead of being fetched from cache.
    """

    def __init__(self, calendar, missions_queryset=None):
        self.calendar = calendar
        # The calendar can start from now plus the slack days or, if the
        # validity period is in the future, from there.
        self.from_ = datetime.utcnow().date() + timedelta(
            days=self.calendar.slack_days
        )
        if self.calendar.valid_from is not None:
            if self.from_ < self.calendar.valid_from:
                self.from_ = self.calendar.valid_from
        self._missions_queryset = missions_queryset
        # Internal data
        self.days = []
        self.missions = {}
        self.current_mission = 0
        self.current_day = 0

    @property
    def missions_queryset(self):
        """The queryset that returns the missions associated to the calendar in
        the proper order.

        The order is first by weekday and then by starting time.
        """
        if self._missions_queryset is None:
            self._missions_queryset = Mission.objects.all().filter(
                calendar_day__calendar=self.calendar,
                shipments__gt=0
            ).order_by('calendar_day__weekday', 'starts')
        return self._missions_queryset

    def initialize(self):
        """Initializes the internal data structures
        """
        # Sets up the internal data structures 'days' and 'missions'.
        #
        # 'days' is a simple list of weekdays defined in the calendar (from 0
        # to 7), while 'missions' maps the day to a list of missions.
        for mission in self.missions_queryset:
            mission_weekday = mission.calendar_day.weekday
            if mission_weekday not in self.days:
                self.days.append(mission_weekday)
            self.missions.setdefault(mission_weekday, []).append(mission)
        # If the calendar defines one or more weekdays that sit before the
        # 'from_' date (in the current week), then we increment the day counter
        # to skip those "invalid" days
        for day in self.days:
            if day < self.from_.isoweekday():
                self.current_day += 1
            else:
                break

    def __iter__(self):
        schedule = self.__class__(
            self.calendar,
            missions_queryset=self.missions_queryset.all()
        )
        schedule.initialize()
        return schedule

    def next(self):
        # If there are no days, there is no next date
        if len(self.days) == 0:
            raise StopIteration()
        # Keep searching the next date up to 256 times: this limit is here to
        # avoid an infinite loop
        while self.current_day < 256:
            # obtains the week "differential" by division
            week = self.current_day / len(self.days)
            # obtains the first valid day as a weekday, and then obtains the
            # list of missions for that day
            day = self.days[self.current_day % len(self.days)]
            mission = self.missions[day][self.current_mission]
            # obtains the date for the first possible mission, and check it is
            # valid (within the calendar limits). If it's not valid, then we
            # don't have any further valid dates (we are searching forward in
            # the future) and we "quit"
            mission_date = get_date(self.from_, day, week)
            if self.calendar.valid_to is not None:
                if mission_date > self.calendar.valid_to:
                    raise StopIteration()
            # increments the internal counter for missions: first we iterate
            # among all missions on a given day, and only after we have
            # exceeded that we do pass to the next day, resetting the mission
            # counter
            self.current_mission += 1
            if self.current_mission >= len(self.missions[day]):
                self.current_mission = 0
                self.current_day += 1
            # Check if there is space to allocate a new shipment: if not, go on
            # with the cycle.
            if mission.remaining_shipments(mission_date) > 0:
                return (mission_date, mission)
        raise StopIteration()


class Shipments(object):
    """An utility to operate on shipments.

    It is zone-bound and allows to:

     * Obtain the next possible shipment
     * Book a shipment
     * Confirm a shipment
     * Clean up non-booked shipments

    As unique initialization parameter takes the zone it is bound to.
    """

    def __init__(self, zone):
        self.today = datetime.utcnow().date()
        self.zone = zone
        # Internal cache of schedulers
        self.schedule_cache = {}

    @property
    def logger(self):
        """Obtains the logger
        """
        return getLogger('shipments.%d' % self.zone.id)

    def get_schedule(self, calendar):
        """Obtains the schedule (``CalendarSchedule`` object) for the given
        calendar.

        Maintains an internal cache to speed up repetitive lookups.
        """
        if calendar.id not in self.schedule_cache:
            self.schedule_cache[calendar.id] = CalendarSchedule(calendar)
        return iter(self.schedule_cache[calendar.id])

    def _iter_exceptions(self, exceptional_calendars):
        """Search within the exceptional calendars provided for the next
        available missions, returning an iterator.

        If a ``condition`` is provided, the date must satisfy it in order to be
        returned: or another one is searched.

        The ``condition`` is a function which takes the projected date as
        parameter and returns a boolean value telling whether it passes or not.
        """
        # iterates over the calendars and returns the available dates
        for calendar in exceptional_calendars:
            try:
                exception_next, exception_mission = next(
                    self.get_schedule(calendar)
                )
            except StopIteration:
                pass
            else:
                yield (exception_next, exception_mission)

    def projected_shipment(self):
        """Returns the next "free" shipping slot as a tuple ``(date, mission)``.

        If no shipping slot can be found, ``Shipments.NoShipment`` is raised.
        """
        # obtains the default calendar. If there is no default calendar, warns.
        try:
            default_calendar = Calendar.objects.all().get(
                zone=self.zone,
                valid_from__isnull=True,
                valid_to__isnull=True
            )
        except Calendar.DoesNotExist:
            self.logger.warning("No default calendar found")
            default_calendar = None
        # Obtains the exceptional calendars iterator, filtering out those that
        # refer to a long time ago
        exceptional_calendars = self._iter_exceptions(
            Calendar.objects.all().filter(
                zone=self.zone,
                valid_to__gte=self.today
            ).order_by('valid_from')
        )
        # Obtains the default schedule if possible
        default_schedule = None
        if default_calendar is not None:
            default_schedule = self.get_schedule(default_calendar)

        # Gets the next date according to the default calendar, if
        # possible.
        #
        # It must not "sit" within an exceptional calendar: if it is so,
        # searches another (posterior) date, up until one is found or the
        # default calendar extinguishes.
        # 'd_date' will be None if there is no date
        d_date, d_mission = (None, None)
        if default_schedule is not None:
            try:
                while True:
                    d_date, d_mission = next(default_schedule)
                    exceptions = Calendar.objects.all().filter(
                        zone=self.zone,
                        valid_from__lte=d_date,
                        valid_to__gte=d_date
                    ).count()
                    if exceptions > 0:
                        d_date, d_mission = (None, None)
                    else:
                        break
            except StopIteration:
                pass
        # obtains the first "exceptional" date available: this is because
        # the exceptional calendar might be either a complete deletion of
        # zones, a shift of days, or it can add more days (extra seasonal
        # work): therefore even if we have a date from the default
        # calendar, we check if there isn't an exception that gets us an
        # earlier date
        try:
            e_date, e_mission = next(exceptional_calendars)
        except StopIteration:
            e_date, e_mission = (None, None)
        # Do we have a date?
        if d_date is not None or e_date is not None:
            # If we have a default date and either the exceptional date is none
            # or it is less than the exceptional date, then returns the one
            # coming from the default calendar. Note that not doing that
            # implies that 'e_date' is not None
            if d_date is not None:
                if e_date is None or e_date >= d_date:
                    return (d_date, d_mission)
            # returns the exceptional date
            return (e_date, e_mission)
        # "no dates, no shipping" -- G. Clooney
        raise self.__class__.NoShipment()

    def obtain_shipment(self, order):
        """Obtains the first available shipment.

        Returns the shipment object: the order it must be associated to is
        passed as the ``order`` parameter.
        """
        date, mission = self.projected_shipment()
        try:
            shipment = Shipment.objects.get(order=order)
            shipment.mission = mission
            shipment.date = date
        except Shipment.DoesNotExist:
            shipment = Shipment(mission=mission, order=order, date=date)
        shipment.save()
        return shipment

    def confirm_shipment(self, order):
        """Confirm the shipment associated to the order ``order``
        """
        shipment = Shipment.objects.all().get(order=order)
        shipment.confirmed = True
        shipment.save()

    def stale_shipments(self, max_days=1):
        """Returns the shipments which were booked ``max_days`` ago and never
        confirmed.
        """
        limit = datetime.utcnow() - timedelta(days=max_days)
        stale = Shipment.objects.all().filter(
            mission__calendar_day__calendar__zone=self.zone,
            booked_on__lt=limit,
            confirmed=False
        )
        for shipment in stale:
            yield shipment

    class NoShipment(StandardError):
        """No shipment was found
        """


# Handle Order Status to confirm shipment
def confirmShipmentForOrder(sender, **kwargs): # pylint:disable=W0613
    """
    Confirm shipment of current order
    if shipping method is 'Calendar shipping'.
    """
    orderstatus = kwargs['instance']
    order = orderstatus.order
    if (orderstatus.status == 'New') and (order.shipping_model == u'Calendar'):
        # confirm shipment for current order
        contact = order.contact
        zone = contact.contactzone.zone
        shipments = Shipments(zone)
        shipments.confirm_shipment(order)

# Handle Order Status to make order status "In Process"
def makeOrderInProcess(sender, **kwargs): # pylint:disable=W0613
    """
    If status is "New", sets status to "In process".
    """
    orderstatus = kwargs['instance']
    if orderstatus.status == 'New':
        # set status to "In process"
        order = orderstatus.order
        order.add_status(status='In Process', notes = unicode(_(u"Order confirmed")))

post_save.connect(confirmShipmentForOrder, sender=OrderStatus)
post_save.connect(makeOrderInProcess, sender=OrderStatus)


def zone_check(sender, **kwargs):
    """Validates the zone after the removal of one of its contained objects.
    """

    try:
        if sender is Mission:
            zone = kwargs['instance'].calendar_day.calendar.zone
        elif sender is CalendarDay:
            zone = kwargs['instance'].calendar.zone
        elif sender is Calendar:
            zone = kwargs['instance'].zone
        else:
            raise ValueError("'sender' can't be %s" % sender)
        zone.validate()
    # If we are removing the zone entirely this goes downward
    # so the checks might fail.
    except ObjectDoesNotExist:
        pass

# Using post_delete else the element is still present and will, in the case of
# missions, make the check pass.
post_delete.connect(zone_check, sender=Calendar)
post_delete.connect(zone_check, sender=CalendarDay)
post_delete.connect(zone_check, sender=Mission)
