import factory
from django.contrib.auth.models import User

from users.models import RequestSignup, OrganizerConfirmation


class UserFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> User:...


class RequestSignUpFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> RequestSignup:...


class OrganizerConfirmationFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> OrganizerConfirmation:...
