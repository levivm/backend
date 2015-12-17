import random

from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, seq

from payments.models import Payment, Fee

fake = Faker()

payment = Recipe(
    Payment,
    payment_type=mommy.generators.gen_from_choices(Payment.PAYMENT_TYPE),
    card_type=mommy.generators.gen_from_choices(Payment.CARD_TYPE),
    transaction_id=fake.uuid4(),
    last_four_digits=mommy.generators.gen_integer(min_int=1000, max_int=9999),
)

fee = Recipe(
    Fee,
    amount=random.random(),
    name=seq('fee'),
)
