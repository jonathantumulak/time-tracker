import django_tables2 as tables

from checkin.models import CheckIn


class TodayCheckInTable(tables.Table):
    """Table for listing users check-ins for the day."""

    checkin_display = tables.Column(
        verbose_name="Check-In",
        accessor="get_check_in_display",
        orderable=False,
    )

    class Meta:
        model = CheckIn
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
        model = CheckIn
        fields = ("hours", "tag", "activity", "timestamp")
        empty_text = "No check-ins found."
        per_page = 10
