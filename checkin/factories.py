import factory
from django.contrib.auth.models import User
from django.utils import timezone
from factory.django import DjangoModelFactory
from factory.helpers import post_generation
from faker import Faker

from checkin.models import (
    CheckIn,
    Tag,
)


faker = Faker()


class UserFactory(DjangoModelFactory):

    username = factory.Faker("user_name")
    email = factory.Faker("email")

    class Meta:
        model = User
        django_get_or_create = ["username"]

    @post_generation
    def password(self, create, extracted, **kwargs):
        password = extracted or "pass"
        self.set_password(password)
        if create:
            self.save()
        self.raw_password = password


class TagFactory(DjangoModelFactory):
    name = factory.Sequence(lambda n: f"Tag-{n}")

    class Meta:
        model = Tag
        django_get_or_create = ["name"]


class CheckInFactory(DjangoModelFactory):

    tag = factory.SubFactory(TagFactory)
    user = factory.SubFactory(UserFactory)
    activity = factory.Sequence(lambda n: f"Activity-{n}")
    timestamp = timezone.now()
    hours = 1

    class Meta:
        model = CheckIn
