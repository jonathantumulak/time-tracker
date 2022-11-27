from decimal import Decimal

from django.test import TestCase
from parameterized import parameterized

from checkin.factories import UserFactory
from checkin.forms import CheckInForm


VALID_CHECKIN_CASES = [
    (5.5, "hrs", "project-x", "fix login issue"),
    (2, "hrs", "learning", "docker"),
    (1, "hr", "project-y", "review vuejs"),
]


class CheckInFormTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory()
        self.form_class = CheckInForm

    @parameterized.expand(VALID_CHECKIN_CASES)
    def test_form_valid(self, hours, hr_string, tag, activity):
        """Test valid form input"""
        input_string = f"{hours} {hr_string} #{tag} {activity}"
        form = self.form_class({"checkin_string": input_string}, user=self.user)
        self.assertTrue(form.is_valid())
        cleaned_data = form.cleaned_data
        self.assertEqual(cleaned_data["hours"], str(hours))
        self.assertEqual(cleaned_data["tag"], tag)
        self.assertEqual(cleaned_data["activity"], activity)

    @parameterized.expand(VALID_CHECKIN_CASES)
    def test_form_save(self, hours, hr_string, tag, activity):
        input_string = f"{hours} {hr_string} #{tag} {activity}"
        form = self.form_class({"checkin_string": input_string}, user=self.user)
        form.is_valid()
        instance = form.save()
        instance.refresh_from_db()
        self.assertEqual(instance.user, self.user)
        self.assertIsNotNone(instance.timestamp)
        self.assertEqual(instance.activity, activity)
        self.assertEqual(instance.hours, Decimal(hours))
        self.assertEqual(instance.tag.name, tag)

    def test_form_invalid(self):
        """Test invalid form input"""

        form = self.form_class({"checkin_string": "Invalid"}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "Invalid check-in input string.")

    def test_form_invalid_empty_string(self):
        """Test invalid form input"""

        form = self.form_class({"checkin_string": ""}, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors["__all__"][0], "Check-in input is empty.")
