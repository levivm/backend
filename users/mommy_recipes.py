from django.contrib.auth.models import User
from faker import Faker
from model_mommy.recipe import Recipe


fake = Faker()

user = Recipe(
    User,
    username=fake.user_name,
    first_name=fake.first_name,
    last_name=fake.last_name,
    email=fake.email,
)
