import mock
from django.core.urlresolvers import reverse
from rest_framework import status

from activities.factories import CalendarFactory
from messages.factories import OrganizerMessageFactory, OrganizerMessageStudentRelationFactory
from messages.models import OrganizerMessage
from messages.serializers import OrganizerMessageSerializer
from orders.factories import OrderFactory
from orders.models import Order
from utils.tests import BaseAPITestCase


class ListAndCreateOrganizerMessageViewTest(BaseAPITestCase):
    def setUp(self):
        super(ListAndCreateOrganizerMessageViewTest, self).setUp()
        self.url = reverse('messages:list_and_create')
        self.calendar = CalendarFactory(activity__organizer=self.organizer)
        self.orders = OrderFactory.create_batch(3, calendar=self.calendar,
                                                status=Order.ORDER_APPROVED_STATUS)
        self.organizer_messages = OrganizerMessageFactory.create_batch(3, organizer=self.organizer)
        self.organizer_message_relation = OrganizerMessageStudentRelationFactory(
            organizer_message=self.organizer_messages[0],
            student=self.student,
        )

    @mock.patch('messages.tasks.SendEmailOrganizerMessageAssistantsTask.s')
    @mock.patch('messages.tasks.SendEmailMessageNotificationTask.s')
    def test_create(self, notification_subtask, message_subtask):
        # Anonymous shouldn't be able to create a message
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student shouldn't be able to create a message
        response = self.student_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should be able to create it
        data = {
            'subject': 'Asunto del mensaje',
            'message': 'Mensaje',
            'calendar_id': self.calendar.id,
        }
        response = self.organizer_client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        organizer_message = OrganizerMessage.objects.get(id=response.json()['id'])
        self.assertEqual(list(organizer_message.students.all()),
                         [o.student for o in self.orders])
        notification_subtask.assert_called_with(organizer_message_id=organizer_message.id)
        message_subtask.assert_called_with(
            organizer_message_id=organizer_message.id,
            calendar_id = self.calendar.id)

    def test_list(self):
        # Anonymous shouldn't be able to create a message
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should be able to list his messages
        response = self.organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         OrganizerMessageSerializer(
                             sorted(self.organizer_messages, key=lambda o: o.pk, reverse=True),
                             many=True).data)

        # Student should be able to list his messages
        response = self.student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         OrganizerMessageSerializer([self.organizer_messages[0]], many=True).data)
