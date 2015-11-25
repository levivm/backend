from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from activities.mommy_recipes import activity
from reviews.models import Review
from students.mommy_recipes import student

fake = Faker()

review = Recipe(
    Review,
    rating=mommy.generators.gen_integer(min_int=0, max_int=5),
    comment=fake.sentence,
    activity=foreign_key(activity),
    author=foreign_key(student),
)
