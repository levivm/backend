import factory

from payments.models import Payment, Fee


class PaymentFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Payment: ...


class FeeFactory(factory.django.DjangoModelFactory):
    def __new__(cls, *args, **kwargs) -> Fee: ...
