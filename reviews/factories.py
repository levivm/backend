import random

import factory

from activities.factories import ActivityFactory
from reviews.models import Review
from students.factories import StudentFactory


class ReviewFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Review

    def __new__(cls, *args, **kwargs):
        return super(ReviewFactory, cls).__new__(*args, **kwargs)

    rating = factory.LazyAttribute(lambda r: random.choice(range(1, 5)))
    comment = factory.Faker('sentence')
    activity = factory.SubFactory(ActivityFactory)
    author = factory.SubFactory(StudentFactory)
