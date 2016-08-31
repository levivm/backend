import factory
import factory.fuzzy

from activities.factories import CalendarFactory
from orders.models import Order, Assistant
from payments.factories import PaymentFactory
from students.factories import StudentFactory


class OrderFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Order

    def __new__(cls, *args, **kwargs):
        return super(OrderFactory, cls).__new__(*args, **kwargs)

    calendar = factory.SubFactory(CalendarFactory)
    student = factory.SubFactory(StudentFactory)
    amount = factory.fuzzy.FuzzyInteger(50000, 1000000)
    quantity = factory.fuzzy.FuzzyInteger(1, 5)
    status = Order.ORDER_APPROVED_STATUS
    payment = factory.SubFactory(PaymentFactory)
    is_free = factory.Faker('boolean', chance_of_getting_true=20)


class AssistantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Assistant

    order = factory.SubFactory(OrderFactory)
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    enrolled = True
