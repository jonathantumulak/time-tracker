from decimal import Decimal

from django.template.defaultfilters import slugify
from django.test import TestCase
from django.utils import timezone

from checkin.factories import UserFactory
from checkin.models import (
    CheckIn,
    Tag,
)


class TagTestCase(TestCase):
    def setUp(self):
        self.tag = Tag.objects.create(name="Tag")

    def test_tag_slug_filled(self):
        """Test slug field will be automatically be added"""
        self.assertEqual(self.tag.slug, slugify(self.tag.name))


class CheckInTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.tag = Tag.objects.create(name="Tag")
        self.checkin = CheckIn.objects.create(
            tag=self.tag, user=self.user, hours=Decimal(1), timestamp=timezone.now(), activity="Activity"
        )

    def test_get_check_in_display(self):
        """Test get_check_in_display if it returns proper format."""
        self.assertEqual(
            self.checkin.get_check_in_display,
            f"{self.checkin.hours.normalize()} hr #{self.tag.name} {self.checkin.activity}",
        )
