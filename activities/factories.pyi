import factory

from activities.models import Activity


class ActivityFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Activity: ...
