import datetime, logging
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase
from django.contrib.sites.models import Site
from ..testing import make_test_order
from .models import (Zone, Calendar, CalendarDay, Mission, Shipment,
                     CalendarSchedule, Shipments)


def get_default_site():
    return Site.objects.get(pk=1)


class CalendarTestBase(TestCase):

    def setUp(self):
        self.zone_1 = Zone(site=get_default_site(), name=u"Zona 1")
        self.zone_1.save()

    def tearDown(self):
        self.zone_1.delete()


class CalendarTest(CalendarTestBase):

    def test_creation(self):
        default = Calendar(zone=self.zone_1,
                           valid_from=None,
                           valid_to=None,
                           slack_days=1)
        default.save()
        festivities = Calendar(zone=self.zone_1,
                               valid_from=datetime.date(2011, 12, 24),
                               valid_to=datetime.date(2012, 1, 1),
                               slack_days=1)
        festivities.save()

    def test_validation_slack_days(self):
        correct = Calendar(zone=self.zone_1,
                           valid_from=None,
                           valid_to=None,
                           slack_days=1)
        correct.full_clean()

        correct_2 = Calendar(zone=self.zone_1,
                             valid_from=None,
                             valid_to=None,
                             slack_days=0)
        correct_2.full_clean()

        wrong = Calendar(zone=self.zone_1,
                         valid_from=None,
                         valid_to=None,
                         slack_days=-1)
        with self.assertRaises(ValidationError):
            wrong.full_clean()

    def test_validation_validity(self):
        correct = Calendar(zone=self.zone_1,
                           valid_from=None,
                           valid_to=None,
                           slack_days=1)
        correct.full_clean()

        correct_2 = Calendar(zone=self.zone_1,
                             valid_from=datetime.date(2011, 12, 24),
                             valid_to=datetime.date(2012, 1, 1),
                             slack_days=1)
        correct_2.full_clean()

        correct_3 = Calendar(zone=self.zone_1,
                             valid_from=datetime.date(2011, 12, 24),
                             valid_to=datetime.date(2011, 12, 24),
                             slack_days=1)
        correct_3.full_clean()

        wrong = Calendar(zone=self.zone_1,
                         valid_from=datetime.date(2012, 1, 1),
                         valid_to=datetime.date(2011, 12, 24),
                         slack_days=1)
        with self.assertRaises(ValidationError):
            wrong.full_clean()

        wrong_2 = Calendar(zone=self.zone_1,
                           valid_from=datetime.date(2011, 12, 24),
                           valid_to=None,
                           slack_days=1)
        with self.assertRaises(ValidationError):
            wrong_2.full_clean()

        wrong_3 = Calendar(zone=self.zone_1,
                           valid_from=None,
                           valid_to=datetime.date(2011, 1, 1),
                           slack_days=1)
        with self.assertRaises(ValidationError):
            wrong_3.full_clean()

    def test_double_default(self):
        default = Calendar(zone=self.zone_1,
                           valid_from=None,
                           valid_to=None,
                           slack_days=1)
        default.full_clean()
        default.save()

        default_copy = Calendar(zone=self.zone_1,
                                valid_from=None,
                                valid_to=None,
                                slack_days=1)
        with self.assertRaises(ValidationError):
            default_copy.full_clean()

    def test_conflicting(self):
        christmas = Calendar(zone=self.zone_1,
                             valid_from=datetime.date(2011, 12, 24),
                             valid_to=datetime.date(2012, 1, 1),
                             slack_days=1)
        christmas.full_clean()
        christmas.save()

        epiphany = Calendar(zone=self.zone_1,
                            valid_from=datetime.date(2012, 1, 6),
                            valid_to=datetime.date(2012, 1, 8),
                            slack_days=1)
        epiphany.full_clean()

        inside = Calendar(zone=self.zone_1,
                          valid_from=datetime.date(2011, 12, 24),
                          valid_to=datetime.date(2011, 12, 26),
                          slack_days=1)
        with self.assertRaises(ValidationError):
            inside.full_clean()

        outside = Calendar(zone=self.zone_1,
                           valid_from=datetime.date(2011, 12, 20),
                           valid_to=datetime.date(2012, 1, 4),
                           slack_days=1)
        with self.assertRaises(ValidationError):
            outside.full_clean()

        same = Calendar(zone=self.zone_1,
                        valid_from=datetime.date(2011, 12, 24),
                        valid_to=datetime.date(2012, 1, 1),
                        slack_days=1)
        christmas.full_clean() # This passes because those with the same pk
                               # are excluded
        with self.assertRaises(ValidationError):
            same.full_clean() # This doesn't (no pk/different pk)

        left = Calendar(zone=self.zone_1,
                        valid_from=datetime.date(2011, 12, 20),
                        valid_to=datetime.date(2011, 12, 26),
                        slack_days=1)
        with self.assertRaises(ValidationError):
            left.full_clean()

        left_touch = Calendar(zone=self.zone_1,
                              valid_from=datetime.date(2011, 12, 20),
                              valid_to=datetime.date(2011, 12, 24),
                              slack_days=1)
        with self.assertRaises(ValidationError):
            left_touch.full_clean()

        right = Calendar(zone=self.zone_1,
                         valid_from=datetime.date(2011, 12, 28),
                         valid_to=datetime.date(2012, 1, 4),
                         slack_days=1)
        with self.assertRaises(ValidationError):
            right.full_clean()

        right_touch = Calendar(zone=self.zone_1,
                               valid_from=datetime.date(2012, 1, 1),
                               valid_to=datetime.date(2012, 1, 4),
                               slack_days=1)
        with self.assertRaises(ValidationError):
            right_touch.full_clean()

        christmas.valid_from = datetime.date(2011, 12, 20)
        christmas.valid_from = datetime.date(2011, 12, 26)
        christmas.full_clean()
        christmas.save()


class CalendarDayTestBase(CalendarTestBase):

    def setUp(self):
        super(CalendarDayTestBase, self).setUp()
        self.default = Calendar(zone=self.zone_1,
                                valid_from=None,
                                valid_to=None,
                                slack_days=1)
        self.default.save()
        self.festivities = Calendar(zone=self.zone_1,
                                    valid_from=datetime.date(2011, 12, 24),
                                    valid_to=datetime.date(2012, 1, 1),
                                    slack_days=1)
        self.festivities.save()

    def tearDown(self):
        self.default.delete()
        self.festivities.delete()
        super(CalendarDayTestBase, self).tearDown()


class CalendarDayTest(CalendarDayTestBase):

    def test_creation(self):
        monday = CalendarDay(calendar=self.default, weekday=1)
        monday.full_clean()
        monday.save()
        thursday = CalendarDay(calendar=self.default, weekday=4)
        thursday.full_clean()
        thursday.save()
        # test conflicting days
        monday_copy = CalendarDay(calendar=self.default, weekday=1)
        monday.full_clean()
        monday.save()
        with self.assertRaises(ValidationError):
            monday_copy.full_clean()


class MissionTestBase(CalendarDayTestBase):

    def setUp(self):
        super(MissionTestBase, self).setUp()
        self.monday = CalendarDay(calendar=self.default, weekday=1)
        self.monday.save()
        self.thursday = CalendarDay(calendar=self.default, weekday=4)
        self.thursday.save()

    def tearDown(self):
        self.monday.delete()
        self.thursday.delete()
        super(MissionTestBase, self).tearDown()


class MissionTest(MissionTestBase):

    def test_creation(self):
        morning = Mission(calendar_day=self.monday,
                          starts=datetime.time(8),
                          ends=datetime.time(11),
                          shipments=50)
        morning.full_clean()
        morning.save()

        afternoon = Mission(calendar_day=self.monday,
                            starts=datetime.time(14),
                            ends=datetime.time(18),
                            shipments=50)
        afternoon.full_clean()

        no_shipments = Mission(calendar_day=self.monday,
                               starts=datetime.time(14),
                               ends=datetime.time(18),
                               shipments=0)
        no_shipments.full_clean()

        invalid_shipments = Mission(calendar_day=self.monday,
                                    starts=datetime.time(14),
                                    ends=datetime.time(18),
                                    shipments=-1)
        with self.assertRaises(ValidationError):
            invalid_shipments.full_clean()

        same_time = Mission(calendar_day=self.monday,
                            starts=datetime.time(14),
                            ends=datetime.time(14),
                            shipments=50)
        same_time.full_clean()

        invalid_time = Mission(calendar_day=self.monday,
                               starts=datetime.time(11),
                               ends=datetime.time(8),
                               shipments=-1)
        with self.assertRaises(ValidationError):
            invalid_time.full_clean()

    def test_conflicting(self):
        morning = Mission(calendar_day=self.monday,
                          starts=datetime.time(8),
                          ends=datetime.time(11),
                          shipments=50)
        morning.full_clean()
        morning.save()

        same = Mission(calendar_day=self.monday,
                       starts=datetime.time(8),
                       ends=datetime.time(11),
                       shipments=50)
        morning.full_clean()
        with self.assertRaises(ValidationError):
            same.full_clean()

        hours = (
            (9, 10),
            (7, 12),
            (7, 10),
            (7, 8),
            (10, 13),
            (11, 13)
        )
        for from_, to in hours:
            conflicting = Mission(calendar_day=self.monday,
                                  starts=datetime.time(from_),
                                  ends=datetime.time(to),
                                  shipments=50)
            with self.assertRaises(ValidationError):
                conflicting.full_clean()

        morning.starts = datetime.time(10)
        morning.ends = datetime.time(12)
        morning.full_clean()
        morning.save()


def monkey_datetime(now):
    class fakedatetime(datetime.datetime):
        @classmethod
        def utcnow(cls):
            return cls(*now)
    return fakedatetime


class TodayTestCase(TestCase):
    # pylint: disable=W0621,W0612

    _now = (2011, 12, 19, 13, 31, 27)

    def setUp(self):
        self.old_datetime = datetime.datetime
        datetime.datetime = monkey_datetime(self._now)
        self.booked_on_field = None
        # pylint:disable=W0212
        # XXX: this is bad, but we need this for tests
        for field in Shipment._meta.fields:
            if field.attname == 'booked_on':
                self.booked_on_field = field
        if self.booked_on_field:
            self.booked_on_field.default = datetime.datetime.utcnow

    def tearDown(self):
        datetime.datetime = self.old_datetime
        if self.booked_on_field:
            self.booked_on_field.default = datetime.datetime.utcnow


class ShipmentTestBase(MissionTestBase, TodayTestCase):

    def setUp(self):
        TodayTestCase.setUp(self)
        MissionTestBase.setUp(self)
        self.monday_morning = Mission(calendar_day=self.monday,
                                      starts=datetime.time(8),
                                      ends=datetime.time(11),
                                      shipments=10)
        self.monday_morning.save()
        self.order = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )

    def tearDown(self):
        self.monday_morning.delete()
        MissionTestBase.tearDown(self)
        TodayTestCase.tearDown(self)


class ShipmentTest(ShipmentTestBase):

    def test_creation(self):
        shipment = Shipment(mission=self.monday_morning,
                            order=self.order,
                            date=datetime.date(2011, 12, 26))
        shipment.save()
        self.assertEqual(shipment.booked_on,
                         datetime.datetime.utcnow())
        self.assertTrue(shipment.confirmed is False)
        # can't have more than one shipment per order
        shipment_2 = Shipment(mission=self.monday_morning,
                              order=self.order,
                              date=datetime.date(2011, 12, 26))
        with self.assertRaises(ValidationError):
            shipment_2.full_clean()
        with self.assertRaises(IntegrityError):
            shipment_2.save()

    def test_remaining_shipments(self):
        self.assertEqual(
            self.monday_morning.remaining_shipments(
                datetime.date(2011, 12, 26)
            ),
            10
        )
        shipment = Shipment(mission=self.monday_morning,
                            order=self.order,
                            date=datetime.date(2011, 12, 26))
        shipment.save()
        self.assertEqual(
            self.monday_morning.remaining_shipments(
                datetime.date(2011, 12, 26)
            ),
            9
        )


class ScheduleTest(TodayTestCase):

    fixtures = [ 'test_schedules.yaml' ]

    def test_simple_iteration(self):
        calendar = Calendar.objects.get(pk=1)
        schedule = CalendarSchedule(calendar)
        schedule.initialize()
        iterator = iter(schedule)
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2011, 12, 21))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2011, 12, 28))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2012, 1, 4))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))

    def test_multimission(self):
        calendar = Calendar.objects.get(pk=3)
        schedule = CalendarSchedule(calendar)
        schedule.initialize()
        iterator = iter(schedule)
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2012, 1, 2))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2012, 1, 2))
        self.assertEqual(mission.starts, datetime.time(15))
        self.assertEqual(mission.ends, datetime.time(18))
        with self.assertRaises(StopIteration):
            __, __ = next(iterator)

    def test_nodata(self):
        calendar = Calendar.objects.get(pk=2)
        schedule = CalendarSchedule(calendar)
        schedule.initialize()
        iterator = iter(schedule)
        with self.assertRaises(StopIteration):
            __, __ = next(iterator)

    def test_startfrom(self):
        calendar = Calendar.objects.get(pk=4)
        schedule = CalendarSchedule(calendar)
        schedule.initialize()
        iterator = iter(schedule)
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2011, 12, 22))
        self.assertEqual(mission.starts, datetime.time(15))
        self.assertEqual(mission.ends, datetime.time(18))
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2011, 12, 26))
        self.assertEqual(mission.starts, datetime.time(15))
        self.assertEqual(mission.ends, datetime.time(18))
        date, mission = next(iterator)
        self.assertEqual(date, datetime.date(2011, 12, 29))
        self.assertEqual(mission.starts, datetime.time(15))
        self.assertEqual(mission.ends, datetime.time(18))


class ShipmentsTest(TodayTestCase):

    fixtures = [ 'test_schedules.yaml' ]

    def setUp(self):
        super(ShipmentsTest, self).setUp()
        self.handler = logging.NullHandler()
        self.logger = logging.getLogger('shipments')
        self.logger.addHandler(self.handler)

    def tearDown(self):
        super(ShipmentsTest, self).setUp()
        self.logger.removeHandler(self.handler)

    def test_projected_simple(self):
        shipments = Shipments(Zone.objects.get(pk=1))
        date, mission = shipments.projected_shipment()
        self.assertEqual(date, datetime.date(2011, 12, 21))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        self.assertEqual(mission.remaining_shipments(date), 2)
        order_1 = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        order_2 = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        shipment_1 = Shipment(
            mission=mission,
            order=order_1,
            date=date
        )
        shipment_1.save()
        shipment_2 = Shipment(
            mission=mission,
            order=order_2,
            date=date
        )
        shipment_2.save()
        date, mission = shipments.projected_shipment()
        self.assertEqual(date, datetime.date(2012, 1, 2))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        order_3 = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        shipment_3 = Shipment(
            mission=mission,
            order=order_3,
            date=date
        )
        shipment_3.save()
        date, mission = shipments.projected_shipment()
        self.assertEqual(date, datetime.date(2012, 1, 2))
        self.assertEqual(mission.starts, datetime.time(15))
        self.assertEqual(mission.ends, datetime.time(18))

    def test_projected_nodata(self):
        shipments = Shipments(Zone.objects.get(pk=4))
        with self.assertRaises(Shipments.NoShipment):
            __, __ = shipments.projected_shipment()

    def test_projected_nodefault(self):
        shipments = Shipments(Zone.objects.get(pk=3))
        date, mission = shipments.projected_shipment()
        self.assertEqual(date, datetime.date(2012, 1, 2))
        self.assertEqual(mission.starts, datetime.time(8))
        self.assertEqual(mission.ends, datetime.time(11))
        order = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        shipment = Shipment(
            mission=mission,
            order=order,
            date=date
        )
        shipment.save()
        with self.assertRaises(Shipments.NoShipment):
            __, __ = shipments.projected_shipment()

    def test_obtain(self):
        shipments = Shipments(Zone.objects.get(pk=1))
        date, mission = shipments.projected_shipment()
        self.assertEqual(mission.remaining_shipments(date), 2)
        order = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        shipment = shipments.obtain_shipment(order)
        self.assertEqual(mission.remaining_shipments(shipment.date), 1)
        self.assertEqual(shipment.date, date)
        self.assertTrue(not shipment.confirmed)

    def test_confirm(self):
        shipments = Shipments(Zone.objects.get(pk=1))
        order = make_test_order(
            site=get_default_site(),
            orderitems=[('formaggio-fresco-di-carmasciano', 5)]
        )
        shipment = shipments.obtain_shipment(order)
        self.assertTrue(not shipment.confirmed)
        shipments.confirm_shipment(order)
        shipment = Shipment.objects.get(order=order)
        self.assertTrue(shipment.confirmed)
