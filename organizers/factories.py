import random

import factory
from django.contrib.auth.models import Group

from organizers.models import Organizer, Instructor, OrganizerBankInfo
from users.factories import UserFactory


class OrganizerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organizer
        
    def __new__(cls, *args, **kwargs):
        return super(OrganizerFactory, cls).__new__(*args, **kwargs)

    user = factory.SubFactory(UserFactory)
    name = factory.Faker('company')
    telephone = factory.Faker('phone_number')
    youtube_video_url = factory.Faker('url')
    website = factory.Faker('url')
    headline = factory.Faker('catch_phrase')
    bio = factory.Faker('bs')

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if create:
            group, _ = Group.objects.get_or_create(name='Organizers')
            self.user.groups.add(group)


class InstructorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Instructor

    full_name = factory.Faker('name')
    bio = factory.Faker('paragraph')
    organizer = factory.SubFactory(OrganizerFactory)
    website = factory.Faker('url')


class OrganizerBankInfoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizerBankInfo

    organizer = factory.SubFactory(OrganizerFactory)
    beneficiary = factory.Faker('name')
    bank = factory.LazyAttribute(lambda n: random.choice([k for k, v in OrganizerBankInfo.BANKS]))
    document_type = factory.LazyAttribute(lambda n: random.choice([k for k, v in OrganizerBankInfo.DOCUMENT_TYPES]))
    document = factory.Faker('ssn')
    account_type = factory.LazyAttribute(lambda n: random.choice([k for k, v in OrganizerBankInfo.ACCOUNT_TYPES]))
    account = factory.Faker('credit_card_number')
