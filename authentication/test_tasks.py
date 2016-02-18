import mock
from django.template import loader
from rest_framework.test import APITestCase

from authentication.models import ResetPasswordToken, ConfirmEmailToken
from authentication.tasks import ChangePasswordNoticeTask, SendEmailResetPasswordTask, \
    SendEmailConfirmEmailTask
from users.factories import UserFactory
from utils.models import EmailTaskRecord


class ChangePasswordNoticeTaskTest(APITestCase):
    """
    Tests for ChangePasswordNoticeTask
    """

    def setUp(self):
        self.user = UserFactory()

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        """
        Test send change password notification successfully
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = ChangePasswordNoticeTask()
        task_id = task.delay(self.user.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='sent').exists())

        context = {
            'name': self.user.first_name
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template(
                'authentication/email/password_has_changed.html').render(),
            'subject': 'Tu contraseña ha cambiado',
            'to': [{'email': self.user.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']
        self.assertTrue(all(item in called_message.items() for item in message.items()))


class SendEmailResetPasswordTaskTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.reset_password = ResetPasswordToken.objects.create(user=self.user)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        """
        Test send change password notification successfully
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailResetPasswordTask()
        task_id = task.delay(self.reset_password.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.user.email,
            status='sent').exists())

        context = {
            'name': self.user.first_name,
            'token': self.reset_password.token,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template(
                'authentication/email/reset_password.html').render(),
            'subject': 'Reinicio de contraseña',
            'to': [{'email': self.user.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']
        self.assertTrue(all(item in called_message.items() for item in message.items()))


class SendEmailConfirmEmailTaskTest(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.confirm_email = ConfirmEmailToken.objects.create(
            user=self.user,
            email='drake.nathan@uncharted.com')

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'drake.nathan@uncharted.com',
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailConfirmEmailTask()
        task_id = task.delay(self.confirm_email.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to='drake.nathan@uncharted.com',
            status='sent').exists())

        context = {
            'name': self.user.first_name,
            'token': self.confirm_email.token,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template(
                'authentication/email/confirm_email.html').render(),
            'subject': 'Confirmación de correo',
            'to': [{'email': 'drake.nathan@uncharted.com'}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']
        self.assertTrue(all(item in called_message.items() for item in message.items()))