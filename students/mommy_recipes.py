import datetime

from django.utils.timezone import utc
from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from locations.mommy_recipes import city
from students.models import Student
from users.mommy_recipes import user


fake = Faker()

def get_birth_date():
    return datetime.datetime.fromtimestamp(fake.unix_time(), tz=utc)

student = Recipe(
    Student,
    user=foreign_key(user),
    city=foreign_key(city),
    gender=mommy.generators.gen_from_choices(Student.GENDER_CHOICES),
    photo=mommy.generators.gen_image_field(),
    birth_date=get_birth_date,
)
