import mock

from django.contrib.auth.models import User
from django.test import override_settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from orders.models import Refund
from orders.tasks import SendEMailStudentRefundTask, SendEmailOrganizerRefundTask
from utils.models import EmailTaskRecord


class SendEMailStudentRefundTaskTest(APITestCase):
    """
    Class to test the task SendEMailStudentRefundTask
    """

    def setUp(self):
        self.user = mommy.make(User, first_name='user', email='user@example.com')
        self.refund = mommy.make(Refund, user=self.user)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_send_email_success(self, send_mail):
        """
        Test sending email success
        """
        send_mail.return_value = [{
            'email': self.refund.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        context = {
            'name': self.refund.user.first_name,
            'order': self.refund.order.id,
            'status': self.refund.status,
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='sent',
            data=context,
            template_name='orders/email/refund_%s_cc_message.txt' % self.refund.status).exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_send_email_rejected(self, send_mail):
        """
        Test sending email rejected
        """
        send_mail.return_value = [{
            'email': self.refund.user.email,
            'status': 'rejected',
            'reject_reason': 'hard-bounce'
        }]

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='rejected',
            reject_reason='hard-bounce').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @override_settings(CELERY_EAGER_PROPAGATES_EXCEPTIONS=False)
    def test_send_email_error(self, send_mail):
        """
        Test sending email error
        """
        send_mail.side_effect = Exception('Hard bounce')

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.user.email,
                status='error',
                reject_reason='Hard bounce').exists())


class SendEMailOrganizerRefundTaskTest(APITestCase):
    """
    Class to test the task SendEMailOrganizerRefundTask
    """

    def setUp(self):
        self.organizer = mommy.make(User, first_name='organizer', email='organizer@example.com')
        self.student = mommy.make(User, first_name='student')
        self.refund = mommy.make(Refund, user=self.student,
                                 order__calendar__activity__organizer__user=self.organizer)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        """
        Test run the task
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.organizer.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailOrganizerRefundTask()
        task_id = task.delay(self.refund.id)

        context = {
            'name': self.organizer.first_name,
            'activity': self.refund.order.calendar.activity.title,
            'student': self.student.get_full_name(),
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.organizer.email,
                status='sent',
                data=context,
                template_name='orders/email/refund_organizer_cc_message.txt').exists())
