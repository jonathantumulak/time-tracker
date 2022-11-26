import datetime

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Sum
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    FormView,
)
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from checkin.filters import CheckInFilter
from checkin.forms import CheckInForm
from checkin.models import CheckIn
from checkin.tables import (
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
        )

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
        )
