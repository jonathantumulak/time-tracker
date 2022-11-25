import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import models
from django.utils import timezone

from checkin.models import (
    CheckIn,
    Tag,
)


class CheckInForm(models.ModelForm):
    checkin_string = forms.CharField(label="Check-In")

    class Meta:
        model = CheckIn
        fields = ["checkin_string"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        checkin_string = cleaned_data.pop("checkin_string", None)

        if not checkin_string:
            raise ValidationError("Check-in input is empty.")

        checkin_string = checkin_string.lower()
        # Match checkin input string into its own variables
        m = re.match(
            r"(?P<hours>\d*\.?\d+) (hr|hrs) #(?P<tag>[a-z0-9]+(?:-[a-z0-9]+)*) (?P<activity>[a-zA-Z0-9_ ]*)",
            checkin_string,
        )
        if m is None:
            raise ValidationError("Invalid check-in input string.")
        self.cleaned_data.update(m.groupdict())
        return self.cleaned_data

    def save(self, commit=True):
        tag, _ = Tag.objects.get_or_create(name=self.cleaned_data["tag"])
        self.instance.user = self.user
        self.instance.date = timezone.now().date()
        self.instance.activity = self.cleaned_data["activity"]
        self.instance.hours = self.cleaned_data["hours"]
        self.instance.tag = tag
        return super().save(commit)
