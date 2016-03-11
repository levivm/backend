import factory

from messages.models import OrganizerMessage, OrganizerMessageStudentRelation
from organizers.factories import OrganizerFactory
from students.factories import StudentFactory


class OrganizerMessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizerMessage

    organizer = factory.SubFactory(OrganizerFactory)
    subject = factory.Faker('sentence')
    message = factory.Faker('text')


class OrganizerMessageStudentRelationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = OrganizerMessageStudentRelation

    organizer_message = factory.SubFactory(OrganizerMessageFactory)
    student = factory.SubFactory(StudentFactory)
