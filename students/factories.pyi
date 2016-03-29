import factory

from students.models import Student


class StudentFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Student: ...
