from django.contrib.auth.models import User
from django.db import models
from django.template.defaultfilters import slugify
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
    date = models.DateField("Date")
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
