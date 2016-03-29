import random
import datetime

import factory
import factory.fuzzy
from django.contrib.auth.models import Group
from django.utils.timezone import now, utc, timedelta

from activities.factories import ActivityFactory
from locations.factories import CityFactory
from students.models import Student, WishList
from users.factories import UserFactory


class StudentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Student

    def __new__(cls, *args, **kwargs):
        return super(StudentFactory, cls).__new__(*args, **kwargs)

    user = factory.SubFactory(UserFactory)
    city = factory.SubFactory(CityFactory)
    gender = factory.LazyAttribute(lambda n: random.choice([k for k, v in Student.GENDER_CHOICES]))
    birth_date = factory.fuzzy.FuzzyDateTime(datetime.datetime(1980, 1, 1, tzinfo=utc), now() - timedelta(days=1825))

    @factory.post_generation
    def group(self, create, extracted, **kwargs):
        if create:
            group, _ = Group.objects.get_or_create(name='Students')
            self.user.groups.add(group)


class WishListFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = WishList

    student = factory.SubFactory(StudentFactory)
    activity = factory.SubFactory(ActivityFactory)
