from django.contrib import admin

from checkin.models import (
    CheckIn,
    Tag,
)


class CheckInAdmin(admin.ModelAdmin):
    list_display = (
        "activity",
        "tag",
        "hours",
        "timestamp",
    )
    list_filter = ("tag",)
    search_fields = (
        "activity",
        "tag__name",
    )
    raw_id_fields = ("tag",)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
    )
    search_fields = (
        "name",
        "slug",
    )


admin.site.register(CheckIn, CheckInAdmin)
admin.site.register(Tag, TagAdmin)
