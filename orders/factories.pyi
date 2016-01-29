import factory

from orders.models import Order


class OrderFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Order: ...
