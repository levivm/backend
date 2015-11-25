import mock

from django.conf import settings
from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Activity
from activities.tasks import SendEmailShareActivityTask
from utils.models import EmailTaskRecord


class SendEmailShareActivityTaskTest(APITestCase):
    """
    Class to test the SendEmailShareActivityTask task
    """

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
        self.user = mommy.make(User)
        self.activity = mommy.make(Activity)

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_email(self, send_mail):
        """
        Test send the email to share the activity
        """

        emails = [mommy.generators.gen_email() for i in range(0, 3)]
        message = 'Hey checa esto!'

        task = SendEmailShareActivityTask()
        task_id = task.delay(self.user.id, self.activity.id, emails=emails, message=message)

        for email in emails:
            self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=email).exists())

        context = {
            'name': self.user.first_name,
            'title': self.activity.title,
            'url': 'https://www.trulli.com/activities/%s/' % self.activity.id,
            'message': message
        }

        calls = [mock.call('activities/email/share_activity_cc', email, context) for email in emails]
        send_mail.assert_has_calls(calls)
