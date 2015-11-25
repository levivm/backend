from django.contrib.auth.models import User
from django.utils.timezone import now
from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from locations.mommy_recipes import city
from users.models import RequestSignup, OrganizerConfirmation

fake = Faker()

user = Recipe(
    User,
    username=fake.user_name,
    first_name=fake.first_name,
    last_name=fake.last_name,
    email=fake.email,
)

request_signup = Recipe(
    RequestSignup,
    email=fake.email, #models.EmailField(max_length=100)
    name=fake.name, #models.CharField(max_length=100)
    telephone=fake.phone_number, #models.CharField(max_length=100)
    city=foreign_key(city), #models.ForeignKey(City)
    document_type=mommy.generators.gen_from_choices(RequestSignup.DOCUMENT_TYPES), #models.CharField(choices=DOCUMENT_TYPES, max_length=5)
    document=fake.ssn, #models.CharField(max_length=100)
)

organizer_confirmation = Recipe(
    OrganizerConfirmation,
    requested_signup=foreign_key(request_signup), #models.OneToOneField(RequestSignup)
    key=fake.word, #models.CharField(verbose_name=_('key'), max_length=64, unique=True)
    sent=now(), #models.DateTimeField(verbose_name=_('sent'), null=True)
)
