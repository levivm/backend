import random

import factory

from activities.factories import CalendarFactory
from orders.models import Order, Assistant, Refund
from payments.factories import PaymentFactory
from students.factories import StudentFactory
from users.factories import UserFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    calendar = factory.SubFactory(CalendarFactory)
    student = factory.SubFactory(StudentFactory)
    amount = factory.LazyAttribute(lambda o: random.choice(range(50000, 1000000)))
    quantity = factory.LazyAttribute(lambda o: random.choice(range(1, 10)))
    status = factory.LazyAttribute(lambda o: random.choice([k for k, v in Order.STATUS]))
    payment = factory.SubFactory(PaymentFactory)
    is_free = factory.Faker('boolean')


class AssistantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assistant

    order = factory.SubFactory(OrderFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    enrolled = factory.Faker('boolean')


class RefundFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Refund

    user = factory.SubFactory(UserFactory)
    order = factory.SubFactory(OrderFactory)
    assistant = factory.SubFactory(AssistantFactory)
    status = factory.LazyAttribute(lambda r: random.choice([k for k, v in Refund.STATUS]))
