from collections import OrderedDict
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Sum
from django.template.defaultfilters import date as _date
from django.urls import reverse
from django_webtest import WebTest
from parameterized import (
    param,
    parameterized,
)

from checkin.factories import (
    CheckInFactory,
    TagFactory,
    UserFactory,
    faker,
)
from checkin.models import CheckIn


class HomeViewTestCase(WebTest):
    """Tests for HomeView"""

    def setUp(self):
        self.user = UserFactory()

    def test_login_success(self):
        """Test success login"""
        response = self.app.get(reverse("checkin:HomeView"))
        self.assertEqual(response.status_code, 200)
        form = response.forms[1]
        form["username"] = self.user.username
        form["password"] = self.user.raw_password
        response = form.submit().follow()
        self.assertTrue(response.context["user"].is_authenticated)

    def test_login_failed(self):
        """Test success login"""
        response = self.app.get(reverse("checkin:HomeView"))
        self.assertEqual(response.status_code, 200)
        form = response.forms[1]
        form["username"] = self.user.username
        form["password"] = "invalid"
        response = form.submit()
        self.assertFalse(response.context["user"].is_authenticated)


class RegisterViewTestCase(WebTest):
    """Tests for RegisterView"""

    def test_register_success(self):
        """Test success login"""
        response = self.app.get(reverse("checkin:RegisterView"))
        self.assertEqual(response.status_code, 200)
        form = response.forms[1]
        password = faker.password()
        form["username"] = "new-user"
        form["password1"] = password
        form["password2"] = password
        response = form.submit()
        self.assertRedirects(response, reverse("checkin:HomeView"))
        self.assertTrue(User.objects.filter(username="new-user").exists())

    def test_login_failed(self):
        """Test success login"""
        response = self.app.get(reverse("checkin:RegisterView"))
        self.assertEqual(response.status_code, 200)
        form = response.forms[1]
        form["username"] = "new-user"
        form["password1"] = "password"
        form["password2"] = "password"
        form.submit()
        self.assertFalse(User.objects.filter(username="new-user").exists())


class CheckinHomeViewTestCase(WebTest):
    """Tests for checkin home view"""

    csrf_checks = False

    def setUp(self):
        self.url = reverse("checkin:CheckinHomeView")
        self.user = UserFactory()

    def test_get_not_logged_in(self):
        """Test get request without user logged-in"""
        response = self.app.get(self.url)
        self.assertRedirects(response, f'{reverse("checkin:HomeView")}?next={self.url}')

    def test_get_logged_in(self):
        """Test get request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        content = response.content.decode("utf-8")
        self.assertIn("Total hours today: 0", content)

    def test_submit_checkin_success(self):
        """Test submitting checkin string"""
        response = self.app.get(self.url, user=self.user)
        form = response.forms["checkin-form"]
        form["checkin_string"] = "5.5 hrs #project-x fix login issue"
        response = form.submit().follow()
        content = response.content.decode("utf-8")
        checkin = CheckIn.objects.get(tag__name="project-x", activity="fix login issue", hours=Decimal(5.5))
        self.assertIsNotNone(checkin)
        self.assertIn("Total hours today: 5.5", content)
        table_row = response.context["table"].rows[0]
        self.assertEqual(table_row.get_cell("checkin_display"), checkin.get_check_in_display)

    def test_submit_checkin_fail(self):
        """Test failed submission of checkin string"""
        response = self.app.get(self.url, user=self.user)
        form = response.forms["checkin-form"]
        form["checkin_string"] = "invalid"
        response = form.submit()
        content = response.content.decode("utf-8")
        self.assertIn("Invalid check-in input string.", content)


class CheckInTestCaseMixin:
    """Checkin testcase mixin to setup test data."""

    def setUp(self):
        super().setUp()
        self.user = UserFactory()
        self.user2 = UserFactory()
        self.tag = TagFactory()
        self.tag2 = TagFactory()
        self.checkin = CheckInFactory(user=self.user, tag=self.tag)
        self.checkin2 = CheckInFactory(user=self.user2, tag=self.tag)

    def assert_checkin_row(self, table_row, checkin):
        self.assertEqual(table_row.get_cell("hours"), checkin.hours)
        self.assertEqual(table_row.get_cell("tag"), checkin.tag)
        self.assertEqual(table_row.get_cell("activity"), checkin.activity)
        self.assertEqual(table_row.get_cell("timestamp"), _date(checkin.timestamp, "SHORT_DATE_FORMAT"))


class MyCheckinViewTestCase(CheckInTestCaseMixin, WebTest):
    """Tests for my checkin view"""

    def setUp(self):
        super().setUp()
        self.url = reverse("checkin:MyCheckinView")

    def test_get_not_logged_in(self):
        """Test get request without user logged-in"""
        response = self.app.get(self.url)
        self.assertRedirects(response, f'{reverse("checkin:HomeView")}?next={self.url}')

    def test_get_logged_in(self):
        """Test get request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

        # only logged-in user's checkins should be listed
        table_rows = response.context["table"].rows
        self.assertEqual(len(table_rows), 1)
        self.assert_checkin_row(table_rows[0], self.checkin)

    def test_filters(self):
        """Test get request with filters"""
        checkin = CheckInFactory(user=self.user, tag=self.tag2)
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

        form = response.forms["filter-form"]
        form["tag"] = self.tag2.id
        response = form.submit()

        table_rows = response.context["table"].rows
        self.assertEqual(len(table_rows), 1)
        self.assert_checkin_row(table_rows[0], checkin)


class MyReportsViewTestCase(CheckInTestCaseMixin, WebTest):
    """Tests for my reports view"""

    def setUp(self):
        super().setUp()
        self.url = reverse("checkin:MyReportsView")

    def assert_chart_data(self, object_list, response_chart_data):
        items = OrderedDict()
        for record in object_list.all():
            label = " - ".join([str(val) for key, val in record.items() if key != "total_hours"])
            items.update(
                {
                    label: float(record["total_hours"].normalize()),
                }
            )
        expected_chart_data = {
            "labels": [key for key in items.keys()],
            "values": [value for value in items.values()],
        }

        self.assertEqual(expected_chart_data, response_chart_data)

    def test_get_not_logged_in(self):
        """Test get request without user logged-in"""
        response = self.app.get(self.url)
        self.assertRedirects(response, f'{reverse("checkin:HomeView")}?next={self.url}')

    def test_get_logged_in(self):
        """Test get request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Select a grouping filter above to show the chart.", response.content.decode("utf-8"))
        self.assertNotIn("chart_data", response.context)

    def test_without_filters(self):
        """Test get request without filters"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

    @parameterized.expand(
        [
            param(
                ["tag__name"],
            ),
            param(
                ["timestamp__date"],
            ),
            param(
                ["tag__name", "timestamp__date"],
            ),
        ]
    )
    def test_with_filters(self, grouping):
        """Test get request with filters"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)
        form = response.forms["filter-form"]
        form["grouping"] = grouping
        response = form.submit()
        self.assertNotIn("Select a grouping filter above to show the chart.", response.content.decode("utf-8"))

        user_checkins = (
            CheckIn.objects.filter(user=self.user)
            .values(*grouping)
            .order_by(*grouping)
            .annotate(total_hours=Sum("hours"))
        )
        self.assert_chart_data(user_checkins, response.context["chart_data"])


class DeleteCheckinView(CheckInTestCaseMixin, WebTest):
    """Tests for delete checkin view"""

    csrf_checks = False

    def setUp(self):
        super().setUp()
        self.url = reverse("checkin:DeleteCheckinView", args=(self.checkin.pk,))

    def test_get_not_logged_in(self):
        """Test get request without user logged-in"""
        response = self.app.get(self.url)
        self.assertRedirects(response, f'{reverse("checkin:HomeView")}?next={self.url}')

    def test_delete_logged_in(self):
        """Test delete request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Are you sure you want to delete this check-in?", response.content.decode("utf-8"))

        form = response.forms[0]
        response = form.submit()
        self.assertRedirects(response, reverse("checkin:MyCheckinView"))
        self.assertFalse(CheckIn.objects.filter(pk=self.checkin.pk).exists())

    def test_delete_not_owned_checkin(self):
        """Test delete checkin request with not owned checkin"""
        user = UserFactory()
        response = self.app.get(self.url, user=user, expect_errors=True)
        self.assertEqual(response.status_code, 404)

    def test_delete_superuser(self):
        """Test delete checkin request with superuser"""
        user = UserFactory(is_superuser=True)
        response = self.app.get(self.url, user=user)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Are you sure you want to delete this check-in?", response.content.decode("utf-8"))

        form = response.forms[0]
        response = form.submit()
        self.assertRedirects(response, reverse("checkin:CheckInListAdminView"))
        self.assertFalse(CheckIn.objects.filter(pk=self.checkin.pk).exists())


class AdminViewsTestMixin:
    def test_get_non_superuser(self):
        """Test get request with non superuser"""
        user = UserFactory()
        response = self.app.get(self.url, user=user, expect_errors=True)
        self.assertEqual(response.status_code, 403)


class CheckInListAdminViewTestCase(AdminViewsTestMixin, MyCheckinViewTestCase):
    """Tests for checkin list admin view"""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.url = reverse("checkin:CheckInListAdminView")

    def assert_checkin_row(self, table_row, checkin):
        super().assert_checkin_row(table_row, checkin)
        self.assertEqual(table_row.get_cell("user"), checkin.user)
        self.assertIn(checkin.get_delete_url(), table_row.get_cell("delete"))

    def test_get_logged_in(self):
        """Test get request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

        # all user's checkins should be listed
        table_rows = response.context["table"].rows
        self.assertEqual(len(table_rows), 2)
        self.assert_checkin_row(table_rows[0], self.checkin)
        self.assert_checkin_row(table_rows[1], self.checkin2)

    def test_filter_by_user(self):
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

        form = response.forms["filter-form"]
        form["user"] = self.checkin2.user
        response = form.submit()
        table_rows = response.context["table"].rows
        self.assertEqual(len(table_rows), 1)
        self.assert_checkin_row(table_rows[0], self.checkin2)


class UserListAdminViewTestCase(CheckInTestCaseMixin, AdminViewsTestMixin, WebTest):
    """Tests for user list admin view"""

    def setUp(self):
        super().setUp()
        self.user.is_superuser = True
        self.user.save()
        self.url = reverse("checkin:UserListAdminView")

    def test_get_not_logged_in(self):
        """Test get request without user logged-in"""
        response = self.app.get(self.url)
        self.assertRedirects(response, f'{reverse("checkin:HomeView")}?next={self.url}')

    def test_get_logged_in(self):
        """Test get request with user logged-in"""
        response = self.app.get(self.url, user=self.user)
        self.assertEqual(response.status_code, 200)

        table_rows = response.context["table"].rows
        self.assertEqual(len(table_rows), 2)
        self.assertIn(self.user.username, table_rows[0].get_cell("username"))
        self.assertEqual(table_rows[0].get_cell("total_hours"), 1)

        self.assertIn(self.user2.username, table_rows[1].get_cell("username"))
        self.assertEqual(table_rows[1].get_cell("total_hours"), 1)
