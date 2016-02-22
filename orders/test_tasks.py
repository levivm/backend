import mandrill
import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader
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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_email_success(self, send_mail):
        """
        Test sending email success
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.refund.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id,
                                                       to=self.user.email,
                                                       status='sent').exists())
        send_mail.assert_called_with(message={
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template(
                    template_name='orders/email/refund_pending_cc_message.txt').render(),
            'subject': 'Información sobre tu reembolso',
            'to': [{'email': self.refund.user.email}],
            'merge_vars': [],
            'global_merge_vars': [],
        })

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_email_rejected(self, send_mail):
        """
        Test sending email rejected
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_email_error(self, send_mail):
        """
        Test sending email error
        """

        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

        send_mail.side_effect = mandrill.Error('Hard bounce')

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.user.email,
                status='error',
                reject_reason='Hard bounce').exists())

        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class SendEMailOrganizerRefundTaskTest(APITestCase):
    """
    Class to test the task SendEMailOrganizerRefundTask
    """

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.organizer = mommy.make(User, first_name='organizer', email='organizer@example.com')
        self.student = mommy.make(User, first_name='student')
        self.refund = mommy.make(Refund, user=self.student,
                                 order__calendar__activity__organizer__user=self.organizer)

    @mock.patch('utils.mixins.mandrill.Messages.send')
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

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.organizer.email,
                status='sent').exists())

        context = {
            'name': self.organizer.first_name,
            'activity': self.refund.order.calendar.activity.title,
            'student': self.student.get_full_name(),
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('orders/email/refund_organizer_cc_message.txt').render(),
            'subject': 'Reembolso aprobado',
            'to': [{'email': self.organizer.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
