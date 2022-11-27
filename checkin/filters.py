import django_filters
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
    Submit,
)
from django import forms
from django.db.models import (
    Exists,
    OuterRef,
    Sum,
)

from checkin.models import Tag


def owned_tags(request):
    if request is None:
        return Tag.objects.all()

    user_checkins = request.user.checkins.filter(tag=OuterRef("pk"))
    return Tag.objects.filter(Exists(user_checkins))


class CheckInFilter(django_filters.FilterSet):
    """Filters for check-ins on my check-ins view"""

    tag = django_filters.ModelChoiceFilter(
        label="Tag",
        queryset=owned_tags,
    )
    timestamp = django_filters.DateFromToRangeFilter(
        label="Date range",
    )
    activity = django_filters.CharFilter(label="Activity", lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = ["tag", "timestamp"]

    @property
    def form(self):
        form = super().form
        form.helper = FormHelper(form)
        form.helper.form_method = "GET"
        form.helper.layout = Layout(
            Field("activity", placeholder="Activity"),
            Field("tag", placeholder="Tag"),
            Field("timestamp", placeholder="MM/DD/YYYY", css_class="datepicker d-inline-block"),
            Submit("submit", "Filter"),
        )
        return form


class GroupingMultipleChoiceFilter(django_filters.MultipleChoiceFilter):
    """Custom filter for grouping queryset and summing total hours."""

    def filter(self, qs, value):
        return qs.values(*value).order_by(*value).annotate(total_hours=Sum("hours"))


class CheckInReportsForm(django_filters.FilterSet):
    """Filters for checkin report view."""

    timestamp = django_filters.DateFromToRangeFilter(
        label="Date range",
    )
    grouping = GroupingMultipleChoiceFilter(
        label="Group by",
        choices=(
            ("tag__name", "Tag"),
            ("timestamp__date", "Date"),
        ),
        widget=forms.CheckboxSelectMultiple(),
    )

    class Meta:
        model = Tag
        fields = ["timestamp"]

    @property
    def form(self):
        form = super().form
        form.helper = FormHelper(form)
        form.helper.form_method = "GET"
        form.helper.layout = Layout(
            Field("timestamp", placeholder="MM/DD/YYYY", css_class="datepicker d-inline-block"),
            InlineCheckboxes("grouping"),
            Submit("submit", "Filter"),
        )
        return form
