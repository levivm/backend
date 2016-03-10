from rest_framework.test import APITestCase

from messages.factories import OrganizerMessageFactory
from messages.models import OrganizerMessage
from messages.serializers import OrganizerMessageSerializer
from organizers.factories import OrganizerFactory
from students.factories import StudentFactory


class OrganizerMessageSerializerTest(APITestCase):

    def setUp(self):
        self.organizer = OrganizerFactory()
        self.students = StudentFactory.create_batch(2)

    def test_create(self):
        data = {
            'subject': 'Subject',
            'message': 'Message',
        }

        serializer = OrganizerMessageSerializer(data=data, context={'organizer': self.organizer})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(OrganizerMessage.objects.count(), 1)
        self.assertTrue(OrganizerMessage.objects.filter(
            organizer=self.organizer,
            subject='Subject',
            message='Message').exists())

    def test_read(self):
        organizer_message = OrganizerMessageFactory(organizer=self.organizer)

        serializer = OrganizerMessageSerializer(organizer_message)

        data = {
            'id': organizer_message.id,
            'subject': organizer_message.subject,
            'message': organizer_message.message,
            'created_at': organizer_message.created_at.isoformat()[:-6] + 'Z',
            'organizer': {
                'id': organizer_message.organizer.id,
                'name': organizer_message.organizer.name,
                'photo': organizer_message.organizer.photo,
            }
        }

        self.assertEqual(serializer.data, data)
