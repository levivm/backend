import random

import factory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from locations.factories import CityFactory
from users.models import RequestSignup, OrganizerConfirmation


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    def __new__(cls, *args, **kwargs):
        return super(UserFactory, cls).__new__(*args, **kwargs)

    username = factory.Faker('user_name')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    password = '19737450'

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        password = kwargs.get('password')
        hash_password = make_password(password=password)
        kwargs['password'] = hash_password
        return super()._create(model_class, *args, **kwargs)


class RequestSignUpFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RequestSignup

    def __new__(cls, *args, **kwargs):
        return super(RequestSignUpFactory, cls).__new__(*args, **kwargs)

    email = factory.Faker('email')
    name = factory.Faker('company')
    telephone = factory.Faker('phone_number')
    city = factory.SubFactory(CityFactory)
    document_type = factory.LazyAttribute(
        lambda r: random.choice([k for k, v in RequestSignup.DOCUMENT_TYPES]))
    document = factory.Faker('ssn')


class OrganizerConfirmationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizerConfirmation

    def __new__(cls, *args, **kwargs):
        return super(OrganizerConfirmationFactory, cls).__new__(*args, **kwargs)

    requested_signup = factory.SubFactory(RequestSignUpFactory)
