from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from activities.mommy_recipes import calendar
from orders.models import Order, Assistant, Refund
from payments.mommy_recipes import payment
from students.mommy_recipes import student
from users.mommy_recipes import user

fake = Faker()

order = Recipe(
    Order,
    calendar=foreign_key(calendar),
    student=foreign_key(student),
    amount=mommy.generators.gen_integer(min_int=50000, max_int=1000000),
    quantity=mommy.generators.gen_integer(min_int=1, max_int=10),
    status=mommy.generators.gen_from_choices(Order.STATUS),
    payment=foreign_key(payment),
    is_free=fake.boolean,
)

assistant = Recipe(
    Assistant,
    order=foreign_key(order),
    first_name=fake.first_name,
    last_name=fake.last_name,
    email=fake.email,
    enrolled=fake.boolean,
)

refund = Recipe(
    Refund,
    user=foreign_key(user),
    order=foreign_key(order),
    assistant=foreign_key(assistant),
    status=mommy.generators.gen_from_choices(Refund.STATUS),
)
