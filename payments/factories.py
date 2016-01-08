import random

import factory

from payments.models import Payment, Fee


class PaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payment

    payment_type = factory.LazyAttribute(lambda p: random.choice([k for k, v in Payment.PAYMENT_TYPE]))
    card_type = factory.LazyAttribute(lambda p: random.choice([k for k, v in Payment.CARD_TYPE]))
    transaction_id = factory.Faker('uuid4')
    last_four_digits = factory.LazyAttribute(lambda p: random.choice(range(1000, 9999)))


class FeeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Fee

    amount = factory.LazyAttribute(lambda f: random.random())
    name = factory.LazyAttribute(lambda f: 'fee %d' % (Fee.objects.count() + 1))
