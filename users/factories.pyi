import factory
from django.contrib.auth.models import User


class UserFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> User: ...
