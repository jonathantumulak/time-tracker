import django_tables2 as tables
from django.db.models import Sum
from django.urls import reverse
from django.utils.html import format_html


class TodayCheckInTable(tables.Table):
    """Table for listing users check-ins for the day."""

    checkin_display = tables.Column(
        verbose_name="Check-In",
        accessor="get_check_in_display",
        orderable=False,
    )

    class Meta:
        fields = ("checkin_display",)
        empty_text = "No check-ins today."


class MyCheckInTable(tables.Table):
    """Table for listing all of a users check-ins."""

    hours = tables.Column()
    tag = tables.Column()
    activity = tables.Column()
    timestamp = tables.DateColumn(verbose_name="Date")
    delete = tables.TemplateColumn(
        verbose_name="Action",
        template_name="checkin/delete_checkin_button.html",
        orderable=False,
    )

    class Meta:
        fields = ("hours", "tag", "activity", "timestamp", "delete")
        empty_text = "No check-ins found."
        per_page = 10


class AdminCheckInTable(MyCheckInTable):
    """Table for check in admin view"""

    user = tables.Column()

    class Meta(MyCheckInTable.Meta):
        fields = ("user",) + MyCheckInTable.Meta.fields


class AdminUserTable(tables.Table):
    """Table for users admin view"""

    username = tables.Column()
    total_hours = tables.Column()

    def order_total_hours(self, queryset, is_descending):
        """Annotate total hours when ordering"""
        queryset = queryset.annotate(total_hours=Sum("checkins__hours")).order_by(
            ("-" if is_descending else "") + "total_hours"
        )
        return (queryset, True)

    def render_username(self, record):
        """
        Render a link to CheckInListAdminView that filters for user
        """
        return format_html(
            '<a href="{}">{}</a>', f"{reverse('checkin:CheckInListAdminView')}?user={record.username}", record.username
        )
