from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import timedelta

from checkin.factories import (
    CheckInFactory,
    TagFactory,
    UserFactory,
)
from checkin.filters import (
    CheckInAdminFilter,
    CheckInFilter,
    CheckInReportsFilter,
    UserAdminFilter,
)


class CheckInFilterTestCaseMixin:
    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.tag = TagFactory()
        self.tag2 = TagFactory()
        self.tag3 = TagFactory()
        self.checkin = CheckInFactory(user=self.user, tag=self.tag)
        self.checkin2 = CheckInFactory(user=self.user, tag=self.tag)
        self.checkin3 = CheckInFactory(user=self.user, tag=self.tag2)


class CheckInFilterTestCase(CheckInFilterTestCaseMixin, TestCase):
    """Checkin filter test case"""

    def test_filter(self):
        """Test default filter"""
        filter_set = CheckInFilter()
        self.assertEqual(filter_set.qs.count(), 3)

    def test_tag_filter(self):
        """Test tag filter"""
        filter_set = CheckInFilter(data={"tag": self.tag.id})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertIn(self.checkin, filter_set.qs)
        self.assertIn(self.checkin2, filter_set.qs)

        filter_set = CheckInFilter(data={"tag": self.tag3.id})
        self.assertEqual(filter_set.qs.count(), 0)

    def test_activity_filter(self):
        """Test activity filter"""
        filter_set = CheckInFilter(data={"activity": self.checkin.activity})
        self.assertEqual(filter_set.qs.count(), 1)
        self.assertIn(self.checkin, filter_set.qs)

        filter_set = CheckInFilter(data={"activity": "not-exists"})
        self.assertEqual(filter_set.qs.count(), 0)

    def test_timestamp_filter(self):
        """Test timestamp filter"""
        filter_set = CheckInFilter(data={"timestamp_before": self.checkin.timestamp.date()})
        self.assertEqual(filter_set.qs.count(), 3)

        one_day_before = self.checkin.timestamp - timedelta(days=1)
        filter_set = CheckInFilter(data={"timestamp_before": one_day_before.date()})
        self.assertEqual(filter_set.qs.count(), 0)

        filter_set = CheckInFilter(data={"timestamp_after": self.checkin.timestamp.date()})
        self.assertEqual(filter_set.qs.count(), 3)

        one_day_after = self.checkin.timestamp + timedelta(days=1)
        filter_set = CheckInFilter(data={"timestamp_after": one_day_after.date()})
        self.assertEqual(filter_set.qs.count(), 0)

        filter_set = CheckInFilter(
            data={"timestamp_before": one_day_after.date(), "timestamp_after": one_day_before.date()}
        )
        self.assertEqual(filter_set.qs.count(), 3)

        two_days_before = self.checkin.timestamp - timedelta(days=2)
        filter_set = CheckInFilter(
            data={"timestamp_before": two_days_before.date(), "timestamp_after": one_day_before.date()}
        )
        self.assertEqual(filter_set.qs.count(), 0)


class CheckInAdminFilterTestCase(CheckInFilterTestCase):
    """Checkin admin filter test case"""

    def test_filter(self):
        """Test default filter"""
        filter_set = CheckInAdminFilter()
        self.assertEqual(filter_set.qs.count(), 3)

    def test_username_filter(self):
        """Test username filter"""
        filter_set = CheckInAdminFilter(data={"user": self.checkin.user.username})
        self.assertEqual(filter_set.qs.count(), 3)
        self.assertIn(self.checkin, filter_set.qs)

        filter_set = CheckInAdminFilter(data={"user": "non-exist"})
        self.assertEqual(filter_set.qs.count(), 0)


class CheckInReportsFilterTestCase(CheckInFilterTestCaseMixin, TestCase):
    """Checkin reports filter test case"""

    def test_filter(self):
        """Test default filter"""
        filter_set = CheckInAdminFilter()
        self.assertEqual(filter_set.qs.count(), 3)

    def test_grouping_by_tag_filter(self):
        """Test grouping by tag name"""
        filter_set = CheckInReportsFilter(data={"grouping": ["tag__name"]})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0]["tag__name"], self.tag.name)
        self.assertEqual(filter_set.qs[0]["total_hours"], Decimal(2))
        self.assertEqual(filter_set.qs[1]["tag__name"], self.tag2.name)
        self.assertEqual(filter_set.qs[1]["total_hours"], Decimal(1))

    def test_grouping_by_date_filter(self):
        """Test grouping by date name"""
        self.checkin.timestamp = timezone.now() - timedelta(days=3)
        self.checkin.save()

        filter_set = CheckInReportsFilter(data={"grouping": ["timestamp__date"]})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0]["timestamp__date"], self.checkin.timestamp.date())
        self.assertEqual(filter_set.qs[0]["total_hours"], Decimal(1))
        self.assertEqual(filter_set.qs[1]["timestamp__date"], self.checkin3.timestamp.date())
        self.assertEqual(filter_set.qs[1]["total_hours"], Decimal(2))

    def test_grouping_by_tag_and_date_filter(self):
        """Test grouping by tag and date name"""

        # create checkin created 3 days before
        old_timestamp = timezone.now() - timedelta(days=3)
        old_checkin = CheckInFactory(tag=self.tag, timestamp=old_timestamp, hours=2)
        CheckInFactory(tag=self.tag, timestamp=old_timestamp, hours=2)
        CheckInFactory(tag=self.tag2, timestamp=old_timestamp, hours=1)

        filter_set = CheckInReportsFilter(data={"grouping": ["tag__name", "timestamp__date"]})
        self.assertEqual(filter_set.qs.count(), 4)
        self.assertEqual(filter_set.qs[0]["tag__name"], self.tag.name)
        self.assertEqual(filter_set.qs[0]["timestamp__date"], old_checkin.timestamp.date())
        self.assertEqual(filter_set.qs[0]["total_hours"], Decimal(4))
        self.assertEqual(filter_set.qs[1]["tag__name"], self.tag.name)
        self.assertEqual(filter_set.qs[1]["timestamp__date"], self.checkin.timestamp.date())
        self.assertEqual(filter_set.qs[1]["total_hours"], Decimal(2))
        self.assertEqual(filter_set.qs[2]["tag__name"], self.tag2.name)
        self.assertEqual(filter_set.qs[2]["timestamp__date"], old_checkin.timestamp.date())
        self.assertEqual(filter_set.qs[2]["total_hours"], Decimal(1))
        self.assertEqual(filter_set.qs[3]["tag__name"], self.tag2.name)
        self.assertEqual(filter_set.qs[3]["timestamp__date"], self.checkin.timestamp.date())
        self.assertEqual(filter_set.qs[3]["total_hours"], Decimal(1))


class AdminUserFilterTestCase(CheckInFilterTestCaseMixin, TestCase):
    """Admin user filter test case"""

    def setUp(self):
        super().setUp()
        self.user2 = UserFactory()
        self.old_timestamp = timezone.now() - timedelta(days=3)
        CheckInFactory(user=self.user2, tag=self.tag)
        CheckInFactory(user=self.user2, tag=self.tag)
        CheckInFactory(user=self.user2, tag=self.tag, timestamp=self.old_timestamp)

    def test_filter(self):
        """Test default filter"""
        filter_set = UserAdminFilter()
        self.assertEqual(filter_set.qs.count(), 2)

    def test_username_filter(self):
        """Test username filter"""
        filter_set = UserAdminFilter(data={"username": self.user.username})
        self.assertEqual(filter_set.qs.count(), 1)
        self.assertIn(self.user, filter_set.qs)

        filter_set = UserAdminFilter(data={"username": "non-exist"})
        self.assertEqual(filter_set.qs.count(), 0)

    def test_checkin_timestamp_filter(self):
        """Test checkin timestamp filter"""
        filter_set = UserAdminFilter(data={"checkin_timestamp_before": self.old_timestamp.date()})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
        self.assertEqual(filter_set.qs[0].total_hours, Decimal(0))
        self.assertEqual(filter_set.qs[1].total_hours, Decimal(1))

        one_day_before = self.old_timestamp - timedelta(days=1)
        filter_set = UserAdminFilter(data={"checkin_timestamp_before": one_day_before.date()})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
        self.assertEqual(filter_set.qs[0].total_hours, Decimal(0))
        self.assertEqual(filter_set.qs[1].total_hours, Decimal(0))

        filter_set = UserAdminFilter(data={"checkin_timestamp_after": self.old_timestamp.date()})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
        self.assertEqual(filter_set.qs[0].total_hours, Decimal(3))
        self.assertEqual(filter_set.qs[1].total_hours, Decimal(3))

        one_day_after = self.old_timestamp + timedelta(days=1)
        filter_set = UserAdminFilter(data={"checkin_timestamp_after": one_day_after.date()})
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
        self.assertEqual(filter_set.qs[0].total_hours, Decimal(3))
        self.assertEqual(filter_set.qs[1].total_hours, Decimal(2))

        filter_set = UserAdminFilter(
            data={"checkin_timestamp_after": one_day_before.date(), "checkin_timestamp_before": one_day_after.date()}
        )
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
        self.assertEqual(filter_set.qs[0].total_hours, Decimal(0))
        self.assertEqual(filter_set.qs[1].total_hours, Decimal(1))

    def test_hours_logged_filter(self):
        """Test hours logged filter"""
        CheckInFactory(user=self.user2, hours=50)

        # must have total_hours annotation
        filter_set = UserAdminFilter(
            data={
                "checkin_timestamp_after": self.old_timestamp.date(),
                "hours_logged_min": 45,
            }
        )
        self.assertEqual(filter_set.qs.count(), 1)
        self.assertEqual(filter_set.qs[0], self.user2)

        filter_set = UserAdminFilter(
            data={
                "checkin_timestamp_after": self.old_timestamp.date(),
                "hours_logged_max": 45,
            }
        )
        self.assertEqual(filter_set.qs.count(), 1)
        self.assertEqual(filter_set.qs[0], self.user)

        filter_set = UserAdminFilter(
            data={
                "checkin_timestamp_after": self.old_timestamp.date(),
                "hours_logged_min": 1,
                "hours_logged_max": 60,
            }
        )
        self.assertEqual(filter_set.qs.count(), 2)
        self.assertEqual(filter_set.qs[0], self.user)
        self.assertEqual(filter_set.qs[1], self.user2)
