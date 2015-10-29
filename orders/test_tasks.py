import mock
from django.conf import settings
from django.contrib.auth.models import User
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
        settings.CELERY_ALWAYS_EAGER = True

        self.user = mommy.make(User, first_name='user', email='user@example.com')
        self.refund = mommy.make(Refund, user=self.user)

    def get_context(self):
        return {
            'name': self.refund.user.first_name,
            'order': self.refund.order.id,
            'status': self.refund.status,
        }

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_email_pending(self, send_mail):
        """
        Test sending email pending
        """
        context = self.get_context()

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.user.email).exists())
        send_mail.assert_called_with(
            'orders/email/refund_%s_cc' % Refund.PENDING_STATUS,
            self.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_email_approved(self, send_mail):
        """
        Test sending email approved
        """
        self.refund.status = Refund.APPROVED_STATUS
        self.refund.save()

        context = self.get_context()

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.user.email).exists())
        send_mail.assert_called_with(
            'orders/email/refund_%s_cc' % Refund.APPROVED_STATUS,
            self.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_email_declined(self, send_mail):
        """
        Test sending email declined
        """
        self.refund.status = Refund.DECLINED_STATUS
        self.refund.save()

        context = self.get_context()

        task = SendEMailStudentRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.user.email).exists())
        send_mail.assert_called_with(
            'orders/email/refund_%s_cc' % Refund.DECLINED_STATUS,
            self.user.email,
            context,
        )


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

    def get_context(self):
        return {
            'name': self.organizer.first_name,
            'activity': self.refund.order.calendar.activity.title,
            'student': self.refund.user.get_full_name(),
        }

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_run(self, send_mail):
        """
        Test run the task
        """
        context = self.get_context()

        task = SendEmailOrganizerRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.organizer.email).exists())
        send_mail.assert_called_with(
            'orders/email/refund_organizer_cc',
            self.organizer.email,
            context,
        )
