import mock
from django.core.urlresolvers import reverse
from rest_framework import status

from activities.factories import CalendarFactory
from messages.factories import OrganizerMessageFactory, OrganizerMessageStudentRelationFactory
from messages.models import OrganizerMessage, OrganizerMessageStudentRelation
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
        self.organizer_messages = OrganizerMessageFactory.create_batch(3, organizer=self.organizer,
                                                                       calendar=self.calendar)
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
            'calendar': self.calendar.id,
        }
        students = [o.student for o in self.orders]
        response = self.organizer_client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        organizer_message = OrganizerMessage.objects.get(id=response.json()['id'])
        self.assertEqual(list(organizer_message.students.all()), students)
        self.assertTrue(self.organizer.user.has_perm('retrieve_message', organizer_message))
        self.assertFalse(self.organizer.user.has_perm('delete_message', organizer_message))
        for student in students:
            self.assertTrue(student.user.has_perm('retrieve_message', organizer_message))
            self.assertTrue(student.user.has_perm('delete_message', organizer_message))
        notification_subtask.assert_called_with(organizer_message_id=organizer_message.id)
        message_subtask.assert_called_with(organizer_message_id=organizer_message.id)

    def test_list(self):

        
        request = mock.MagicMock()
        request.user = self.student.user

        # Anonymous shouldn't be able to create a message
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should be able to list his messages
        response = self.organizer_client.get(self.url,
                                             data={'activity_id': self.calendar.activity.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         OrganizerMessageSerializer(
                             sorted(self.organizer_messages, key=lambda o: o.pk, reverse=True),
                             many=True).data)

        # Student should be able to list his messages
        response = self.student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         OrganizerMessageSerializer([self.organizer_messages[0]], many=True,
                            context={'request':request}).data)


class RetrieveDestroyOrganizerMessageViewTest(BaseAPITestCase):

    def setUp(self):
        super(RetrieveDestroyOrganizerMessageViewTest, self).setUp()
        self.organizer_message = OrganizerMessageFactory(organizer=self.organizer)
        self.organizer_message_relation = OrganizerMessageStudentRelationFactory(
            organizer_message=self.organizer_message,
            student=self.student)
        self.url = reverse('messages:retrieve_and_destroy', args=[self.organizer_message.id])

    def test_retrieve(self):

        request = mock.MagicMock()
        request.user = self.student.user

        # Anonymous shouldn't be able to retrieve an organizer message
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should be allowed to retrieve an organizer message
        response = self.student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, 
                         OrganizerMessageSerializer(self.organizer_message,
                                                    context={'request':request}).data)

        # Another student shouldn't be allowed to get the data
        response = self.another_student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should be allowed to ge the data
        response = self.organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrganizerMessageSerializer(self.organizer_message).data)

        # Another organizer shouldn't be allowed to get the data
        response = self.another_organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_destroy(self):
        # Anonymous should get unauthorized response
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer shouldn't be allowed to delete a message
        response = self.organizer_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Another student shouldn't be allowed to delete a message
        response = self.another_student_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should be allowed to delete an organizer message relation
        response = self.student_client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(OrganizerMessage.objects.filter(
            id=self.organizer_message.id).exists())
        self.assertFalse(OrganizerMessageStudentRelation.objects.filter(
            id=self.organizer_message_relation.id).exists())

class UpdateOrganizerMessageViewTest(BaseAPITestCase):

    def setUp(self):
        super(UpdateOrganizerMessageViewTest, self).setUp()
        self.organizer_message = OrganizerMessageFactory(organizer=self.organizer)
        self.organizer_message_relation = OrganizerMessageStudentRelationFactory(
            organizer_message=self.organizer_message,
            student=self.student)
        self.url = reverse('messages:mark_as_read', args=[self.organizer_message.id])

    def test_read(self):
        # Anonymous shouldn't be able to update an organizer message
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should be allowed to mark as read an organizer message
        response = self.student_client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Another student shouldn't be allowed to update the data
        response = self.another_student_client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Organizer shouldn't be allowed to ge the data
        response = self.organizer_client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)








