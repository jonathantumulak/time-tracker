import django_tables2 as tables
from django.db.models import Sum


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
    user = tables.Column()

    class Meta(MyCheckInTable.Meta):
        fields = ("user", "hours", "tag", "activity", "timestamp")


class AdminUserTable(tables.Table):
    username = tables.Column()
    total_hours = tables.Column()

    def order_total_hours(self, queryset, is_descending):
        queryset = queryset.annotate(total_hours=Sum("checkins__hours")).order_by(
            ("-" if is_descending else "") + "total_hours"
        )
        return (queryset, True)
