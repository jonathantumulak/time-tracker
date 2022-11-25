from django.contrib.auth.forms import (
    AuthenticationForm,
    UserCreationForm,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    FormView,
    TemplateView,
)


class BaseViewMixin:
    page_title = "Check-In"

    def get_context_data(self):
        ctx = super().get_context_data()
        ctx.update(
            {
                "page_title": self.page_title,
            }
        )

        return ctx


class HomeView(BaseViewMixin, FormView):
    form_class = AuthenticationForm
    template_name = "checkin/login.html"
    page_title = "Check-In | Login"

    def get_success_url(self):
        return reverse("checkin:CheckinHomeView")

    def dispatch(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect("checkin:CheckinHomeView")
        return super().dispatch(*args, **kwargs)


class RegisterView(BaseViewMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "checkin/register.html"
    page_title = "Check-In | Register"

    def get_success_url(self):
        return reverse("checkin:home")


class CheckinHomeView(BaseViewMixin, LoginRequiredMixin, TemplateView):
    # form_class = UserCreationForm
    template_name = "checkin/home.html"
    page_title = "Check-In App"


class ListCheckinView(BaseViewMixin, LoginRequiredMixin, TemplateView):
    # form_class = UserCreationForm
    template_name = "checkin/checkins.html"
    page_title = "Check-Ins | View"
