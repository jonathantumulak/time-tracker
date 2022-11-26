import django_filters
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    Field,
    Layout,
    Submit,
)
from django.db.models import (
    Exists,
    OuterRef,
)

from checkin.models import Tag


def owned_tags(request):
    if request is None:
        return Tag.objects.all()

    user_checkins = request.user.checkins.filter(tag=OuterRef("pk"))
    return Tag.objects.filter(Exists(user_checkins))


class CheckInFilter(django_filters.FilterSet):
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
