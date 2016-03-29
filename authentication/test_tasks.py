import mock
from django.template import loader
from rest_framework.test import APITestCase

from authentication.models import ResetPasswordToken, ConfirmEmailToken
from authentication.tasks import ChangePasswordNoticeTask, SendEmailResetPasswordTask, \
    SendEmailConfirmEmailTask, SendEmailHasChangedTask
from users.factories import UserFactory
from utils.models import EmailTaskRecord


class ChangePasswordNoticeTaskTest(APITestCase):
    """
    Tests for ChangePasswordNoticeTask
    """

    def setUp(self):
        self.user = UserFactory()

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        """
        Test send change password notification successfully
        """

        send_mail.return_value = [{
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = ChangePasswordNoticeTask()
        task_id = task.delay(self.user.id)

        context = {}

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='sent',
            data=context,
            template_name='authentication/email/password_has_changed.html').exists())


class SendEmailResetPasswordTaskTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.reset_password = ResetPasswordToken.objects.create(user=self.user)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        """
        Test send change password notification successfully
        """

        send_mail.return_value = [{
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailResetPasswordTask()
        task_id = task.delay(self.reset_password.id)

        context = {
            'url': self.reset_password.get_token_url(),
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='sent',
            data=context,
            template_name='authentication/email/reset_password.html').exists())


class SendEmailConfirmEmailTaskTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.confirm_email = ConfirmEmailToken.objects.create(
            user=self.user,
            email='drake.nathan@uncharted.com')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        send_mail.return_value = [{
            'email': 'drake.nathan@uncharted.com',
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailConfirmEmailTask()
        task_id = task.delay(self.confirm_email.id)

        context = {
            'name': self.user.first_name,
            'url': self.confirm_email.get_token_url(),
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to='drake.nathan@uncharted.com',
            status='sent',
            data=context,
            template_name='authentication/email/confirm_email.html').exists())


class SendEmailHasChangedTaskTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.confirm_email = ConfirmEmailToken.objects.create(
            user=self.user,
            email='drake.nathan@uncharted.com',
        )

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail):
        send_mail.return_value = [{
            'email': 'drake.nathan@uncharted.com',
            'status': 'sent',
            'reject_reason': None,
        }]

        task = SendEmailHasChangedTask()
        task_id = task.delay(confirm_email_id=self.confirm_email.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to='drake.nathan@uncharted.com',
            status='sent',
            data={},
            template_name='authentication/email/email_has_changed.html').exists())


