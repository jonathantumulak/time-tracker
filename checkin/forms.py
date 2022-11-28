import re
from decimal import Decimal

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.forms import models
from django.utils import timezone
from django.utils.html import escape

from checkin.models import (
    CheckIn,
    Tag,
)


class CheckInForm(models.ModelForm):
    """Form to create new check-ins"""

    checkin_string = forms.CharField(
        help_text=escape("Use the following format: <number> [hr | hrs] #<tag> <activities>")
    )

    class Meta:
        model = CheckIn
        fields = ["checkin_string"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.form_id = "checkin-form"
        self.helper.form_show_labels = False
        self.helper.add_input(Submit("submit", "Submit"))

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
        self.instance.timestamp = timezone.now()
        self.instance.activity = self.cleaned_data["activity"]
        self.instance.hours = Decimal(self.cleaned_data["hours"])
        self.instance.tag = tag
        return super().save(commit)
