import django_filters
from crispy_forms.bootstrap import InlineCheckboxes
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
    Submit,
)
from django import forms
from django.contrib.auth.models import User
from django.db.models import (
    DecimalField,
    Exists,
    OuterRef,
    Subquery,
    Sum,
)

from checkin.models import (
    CheckIn,
    Tag,
)


def owned_tags(request):
    """Return a queryset of tags that the user has check-ins for."""
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


class CheckInReportsFilter(django_filters.FilterSet):
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


class UserCheckInDateRangeFilter(django_filters.DateFromToRangeFilter):
    """Custom filter for user check-ins and annotating total hours."""

    def filter(self, qs, value):
        if not value:
            return qs

        if value.start is not None and value.stop is not None:
            self.lookup_expr = "range"
            value = (value.start, value.stop)
        elif value.start is not None:
            self.lookup_expr = "gte"
            value = value.start
        elif value.stop is not None:
            self.lookup_expr = "lte"
            value = value.stop

        lookup = "%s__%s" % (self.field_name, self.lookup_expr)

        # filter checkins for user on date range and annotate total hours
        # to user query
        user_checkins_for_date_range = (
            CheckIn.objects.filter(user=OuterRef("id"), **{lookup: value})
            .order_by()
            .values("user")
            .annotate(total_hours=Sum("hours"))
            .values("total_hours")
        )
        return qs.annotate(total_hours=Subquery(user_checkins_for_date_range, output_field=DecimalField()))


class AdminUserFilter(django_filters.FilterSet):
    """Filters for user list view for admins"""

    username = django_filters.CharFilter(label="Username", lookup_expr="icontains")
    checkin_timestamp = UserCheckInDateRangeFilter(label="Checkin date range", field_name="timestamp")
    hours_logged = django_filters.RangeFilter(
        label="Hours logged",
        field_name="total_hours",
    )

    class Meta:
        model = User
        fields = ["username"]

    @property
    def form(self):
        form = super().form
        form.helper = FormHelper(form)
        form.helper.form_method = "GET"
        form.helper.layout = Layout(
            Field("username"),
            Field("checkin_timestamp", placeholder="MM/DD/YYYY", css_class="datepicker d-inline-block"),
            Field("hours_logged"),
            Submit("submit", "Filter"),
        )
        return form
