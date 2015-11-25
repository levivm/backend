from faker import Faker
from model_mommy import mommy
from model_mommy.recipe import Recipe, foreign_key

from organizers.models import Organizer, Instructor, OrganizerBankInfo
from users.mommy_recipes import user


fake = Faker()

organizer = Recipe(
    Organizer,
    user=foreign_key(user),
    name=fake.company,
    photo=mommy.generators.gen_image_field,
    telephone=fake.phone_number,
    youtube_video_url=fake.url,
    website=fake.url,
    headline=fake.catch_phrase,
    bio=fake.bs,
)

instructor = Recipe(
    Instructor,
    full_name=fake.name,
    bio=fake.paragraph,
    photo=fake.image_url,
    organizer=foreign_key(organizer),
    website=fake.url,
)

organizer_bank_info = Recipe(
    OrganizerBankInfo,
    organizer=foreign_key(organizer),
    beneficiary=fake.name,
    bank=mommy.generators.gen_from_choices(OrganizerBankInfo.BANKS),
    document_type=mommy.generators.gen_from_choices(OrganizerBankInfo.DOCUMENT_TYPES),
    document=fake.ssn,
    account_type=mommy.generators.gen_from_choices(OrganizerBankInfo.ACCOUNT_TYPES),
    account=fake.credit_card_number,
)
