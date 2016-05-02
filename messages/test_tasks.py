import mock
from django.conf import settings
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory
from messages.factories import OrganizerMessageStudentRelationFactory, OrganizerMessageFactory
from messages.tasks import SendEmailMessageNotificationTask, \
    SendEmailOrganizerMessageAssistantsTask, AssociateStudentToMessagesTask
from messages.models import OrganizerMessageStudentRelation
from students.factories import StudentFactory
from orders.factories import AssistantFactory
from orders.models import Order
from organizers.factories import OrganizerFactory
from utils.models import EmailTaskRecord


class SendEmailMessageNotificationTaskTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()
        self.organizer_message = OrganizerMessageFactory(organizer=self.organizer)
        self.organizer_message_student = OrganizerMessageStudentRelationFactory.create_batch(
            size=3,
            organizer_message = self.organizer_message)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        emails = [oms.student.user.email for oms in self.organizer_message_student]
        send_mail.return_value = [{
            'email': email,
            'status': 'sent',
            'reject_reason': None
        } for email in emails]

        task = SendEmailMessageNotificationTask()
        task_id = task.delay(
            organizer_message_id=self.organizer_message.id)

        context = {
            'organizer': self.organizer.name,
            'url': '{base}student/dashboard/messages/{id}'.format(
                base=settings.FRONT_SERVER_URL,
                id=self.organizer_message.id)
        }

        for messages in self.organizer_message_student:
            data = {**context, 'name': messages.student.user.first_name}
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=messages.student.user.email,
                status='sent',
                template_name='messages/email/student_notification.html',
                data=data
            ).exists())


class SendEmailOrganizerMessageAssistantsTaskTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()
        self.calendar = CalendarFactory(activity__organizer=self.organizer)
        self.organizer_message = OrganizerMessageFactory(calendar=self.calendar)
        self.assistants = AssistantFactory.create_batch(
            size=3,
            order__calendar=self.calendar,
            order__status=Order.ORDER_APPROVED_STATUS,
            enrolled=True)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        emails = [a.email for a in self.assistants]
        send_mail.return_value = [{
            'email': email,
            'status': 'sent',
            'reject_reason': None,
        } for email in emails]

        task = SendEmailOrganizerMessageAssistantsTask()
        task_id = task.delay(
            organizer_message_id=self.organizer_message.id)

        context = {
            'organizer': self.organizer_message.organizer.name,
            'message': self.organizer_message.message,
        }

        for assistant in self.assistants:
            data = {**context, 'name': assistant.first_name}
            self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=assistant.email,
                status='sent',
                template_name='messages/email/assistant_message.html',
                data=data
            ).exists())


class AssociateStudentToMessagesTaskTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()
        self.student = StudentFactory()
        self.calendar = CalendarFactory(activity__organizer=self.organizer)
        self.organizer_message = OrganizerMessageFactory(calendar=self.calendar)
        self.assistants = AssistantFactory.create_batch(
            size=3,
            order__calendar=self.calendar,
            order__student=self.student,
            order__status=Order.ORDER_APPROVED_STATUS,
            enrolled=True)

    def test_run(self):
        task = AssociateStudentToMessagesTask()
        task_id = task.delay(self.calendar.id, self.student.id)
        self.assertTrue(OrganizerMessageStudentRelation.objects.\
            filter(student=self.student.id, organizer_message__calendar=self.calendar).exists())





