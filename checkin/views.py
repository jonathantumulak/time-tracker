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

from checkin.forms import CheckInForm


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
        return reverse("checkin:HomeView")


class CheckinHomeView(BaseViewMixin, LoginRequiredMixin, FormView):
    # form_class = UserCreationForm
    template_name = "checkin/home.html"
    page_title = "Check-In App"
    form_class = CheckInForm

    def get_success_url(self):
        return reverse("checkin:CheckinHomeView")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        return super().form_valid(form)


class ListCheckinView(BaseViewMixin, LoginRequiredMixin, TemplateView):
    # form_class = UserCreationForm
    template_name = "checkin/checkins.html"
    page_title = "Check-Ins | View"
