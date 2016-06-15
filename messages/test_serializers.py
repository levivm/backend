from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory
from messages.factories import OrganizerMessageFactory
from messages.models import OrganizerMessage
from messages.serializers import OrganizerMessageSerializer
from organizers.factories import OrganizerFactory
from students.factories import StudentFactory


class OrganizerMessageSerializerTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()
        self.students = StudentFactory.create_batch(2)
        self.calendar = CalendarFactory(activity__organizer=self.organizer)

    def test_create(self):
        data = {
            'subject': 'Subject',
            'message': 'Message',
            'calendar': self.calendar.id,
        }

        serializer = OrganizerMessageSerializer(data=data, context={'organizer': self.organizer,
                                                                    'calendar': self.calendar})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(OrganizerMessage.objects.count(), 1)
        self.assertTrue(OrganizerMessage.objects.filter(
            organizer=self.organizer,
            subject='Subject',
            message='Message').exists())

    def test_read(self):
        organizer_message = OrganizerMessageFactory(organizer=self.organizer,
                                                    calendar=self.calendar)

        serializer = OrganizerMessageSerializer(organizer_message)

        data = {
            'id': organizer_message.id,
            'subject': organizer_message.subject,
            'message': organizer_message.message,
            'created_at': organizer_message.created_at.isoformat()[:-6] + 'Z',
            'organizer': {
                'id': organizer_message.organizer.id,
                'name': organizer_message.organizer.name,
                'photo': None,
            },
            'calendar': self.calendar.id,
            'activity': self.calendar.activity.title,
            'initial_date': self.calendar.initial_date.isoformat()[:-6] + 'Z',
            'is_read': None 
        }

        self.assertEqual(serializer.data, data)

    def test_validate_organizer(self):
        data = {
            'subject': 'Subject',
            'message': 'Message',
            'calendar': self.calendar.id,
        }

        with self.assertRaisesMessage(ValidationError,
                                      "{'organizer': ['El organizador es requerido.']}"):
            serializer = OrganizerMessageSerializer(data=data)
            serializer.is_valid(raise_exception=True)
