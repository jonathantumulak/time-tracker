import datetime
from collections import OrderedDict

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    FormView,
)
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from checkin.filters import (
    CheckInAdminFilter,
    CheckInFilter,
    CheckInReportsFilter,
    UserAdminFilter,
)
from checkin.forms import CheckInForm
from checkin.models import CheckIn
from checkin.tables import (
    AdminCheckInTable,
    AdminUserTable,
    MyCheckInTable,
    TodayCheckInTable,
)


class BaseViewMixin:
    """Base view mixin to add page title into context"""

    page_title = "Check-In"

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(
            {
                "page_title": self.page_title,
            }
        )

        return ctx


class SuperUserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """View mixin for allowing a logged in superuser access."""

    def test_func(self):
        return self.request.user.is_superuser


class HomeView(BaseViewMixin, LoginView):
    """Homepage that serves as login page."""

    template_name = "checkin/login.html"
    page_title = "Check-In | Login"

    def get_success_url(self):
        return reverse("checkin:CheckinHomeView")

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("checkin:CheckinHomeView")
        return super().dispatch(*args, **kwargs)


class RegisterView(BaseViewMixin, CreateView):
    """View for registering new users."""

    model = User
    form_class = UserCreationForm
    template_name = "checkin/register.html"
    page_title = "Check-In | Register"

    def get_success_url(self):
        return reverse("checkin:HomeView")


class CheckinHomeView(BaseViewMixin, LoginRequiredMixin, SingleTableMixin, FormView):
    """Homepage for logged-in users."""

    template_name = "checkin/home.html"
    page_title = "Check-In App"
    form_class = CheckInForm
    table_class = TodayCheckInTable

    @property
    def queryset(self):
        return CheckIn.objects.filter(
            user=self.request.user,
            timestamp__date=datetime.date.today(),
        ).select_related("tag")

    def get_queryset(self):
        return self.queryset

    def get_success_url(self):
        return reverse("checkin:CheckinHomeView")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx.update(
            {
                "total_today": self.queryset.aggregate(total_today=Sum("hours"))["total_today"] or 0,
            }
        )

        return ctx


class MyCheckinView(BaseViewMixin, LoginRequiredMixin, SingleTableMixin, FilterView):
    """View to list all of logged in user's check-ins"""

    template_name = "checkin/my_checkins.html"
    page_title = "My Check-Ins"
    table_class = MyCheckInTable
    model = CheckIn
    filterset_class = CheckInFilter

    @property
    def queryset(self):
        return CheckIn.objects.filter(
            user=self.request.user,
        ).select_related("tag")


class MyReportsView(BaseViewMixin, LoginRequiredMixin, FilterView):
    """View to show basic reports for a users check-ins."""

    template_name = "checkin/my_reports.html"
    model = CheckIn
    filterset_class = CheckInReportsFilter
    page_title = "Check-In | Reports"

    @property
    def queryset(self):
        return CheckIn.objects.filter(
            user=self.request.user,
        )

    def get_context_data(self, *args, **kwargs):
        ctx = super().get_context_data(*args, **kwargs)
        ctx["has_grouping_query"] = "grouping" in self.request.GET
        if ctx["has_grouping_query"]:
            object_list = ctx["object_list"]
            ctx["chart_data"] = self._build_chart_data(object_list)

        return ctx

    def _build_chart_data(self, object_list):
        """Format object_list data to be accepted by chart.js."""
        items = OrderedDict()
        for record in object_list.all():
            label = " - ".join([str(val) for key, val in record.items() if key != "total_hours"])
            items.update(
                {
                    label: float(record["total_hours"].normalize()),
                }
            )
        return {
            "labels": [key for key in items.keys()],
            "values": [value for value in items.values()],
        }


class DeleteCheckinView(BaseViewMixin, LoginRequiredMixin, DeleteView):
    template_name = "checkin/delete_checkin.html"

    @property
    def queryset(self):
        queryset = CheckIn.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        return queryset

    def get_success_url(self):
        if self.request.user.is_superuser:
            return reverse("checkin:CheckInListAdminView")
        else:
            return reverse("checkin:MyCheckinView")


class CheckInListAdminView(BaseViewMixin, SuperUserRequiredMixin, SingleTableMixin, FilterView):
    """Admin view for listing all check-ins"""

    template_name = "checkin/admin_checkins.html"
    page_title = "All Check-Ins"
    table_class = AdminCheckInTable
    model = CheckIn
    filterset_class = CheckInAdminFilter

    @property
    def queryset(self):
        return CheckIn.objects.all().select_related("tag")


class UserListAdminView(BaseViewMixin, SuperUserRequiredMixin, SingleTableMixin, FilterView):
    """Admin view for listing all check-ins"""

    template_name = "checkin/admin_users.html"
    page_title = "All Users"
    table_class = AdminUserTable
    model = User
    filterset_class = UserAdminFilter

    @property
    def queryset(self):
        return User.objects.all()

    def get_queryset(self):
        return self.queryset.annotate(total_hours=Sum("checkins__hours"))
