import mandrill
import mock
from django.conf import settings
from django.contrib.auth.models import User
from django.template import loader

from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory, ActivityFactory
from activities.tasks import SendEmailShareActivityTask, SendEmailCalendarTask
from utils.models import EmailTaskRecord


class SendEmailCalendarTaskTest(APITestCase):
    """
    Class to test the SendEmailCalendarTask task
    """

    def setUp(self):
        self.calendar = CalendarFactory()

    @mock.patch('activities.tasks.')
    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailCalendarTask()
        result = task.apply((self.CALENDAR_ID,))
        self.assertEqual(result.result, 'Task scheduled')


class SendEmailShareActivityTaskTest(APITestCase):
    """
    Class to test the SendEmailShareActivityTask task
    """

    def setUp(self):
        self.user = mommy.make(User)
        self.activity = ActivityFactory()

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        """
        Test send the email to share the activity when it's success
        """

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': e,
            'status': 'sent',
            'reject_reason': None
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                    task_id=task_id,
                    to=email,
                    status='sent').exists())

    @mock.patch('utils.mixins.MandrillMixin.send_mail')
    def test_rejected(self, send_mail):
        """
        Test send the email to share the activity when it's rejected
        """

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': e,
            'status': 'rejected',
            'reject_reason': 'invalid-sender'
        } for e in emails]

        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                    task_id=task_id,
                    to=email,
                    status='rejected',
                    reject_reason='invalid-sender').exists())


    @mock.patch('utils.mixins.MandrillMixin.send_mail')
    def test_error(self, send_mail):
        """
        Test send the email to share the activity when it's error
        """

        settings.CELERY_EAGER_PROPAGATES_EXCEPTIONS = False

        emails = [mommy.generators.gen_email() for _ in range(0, 3)]
        message = 'Hey checa esto!'

        send_mail.side_effect = mandrill.Error('No subaccount exists with the id customer-123')

        # with self.assertRaises(mandrill.Error):
        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(
                    task_id=task_id,
                    to=email,
                    status='error',
                    reject_reason='No subaccount exists with the id customer-123').exists())
