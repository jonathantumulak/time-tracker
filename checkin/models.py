from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django_extensions.db.models import TimeStampedModel


class Tag(models.Model):
    name = models.CharField("Name", max_length=255, unique=True)
    slug = models.SlugField(editable=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)


class CheckIn(TimeStampedModel):
    user = models.ForeignKey(
        User,
        related_name="checkins",
        on_delete=models.CASCADE,
    )
    hours = models.DecimalField("Hours", default=0, max_digits=3, decimal_places=2)
    timestamp = models.DateTimeField("Timestamp")
    tag = models.ForeignKey(
        Tag,
        related_name="checkins",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    activity = models.CharField("Activity", max_length=255)

    def __str__(self):
        return f"#{self.tag} | {self.activity}"

    @property
    def get_check_in_display(self):
        hour_string = "hr" if self.hours == 1 else "hrs"
        return f"{self.hours.normalize()} {hour_string} #{self.tag.name} {self.activity}"

    def get_delete_url(self):
        return reverse("checkin:DeleteCheckinView", args=(self.pk,))
