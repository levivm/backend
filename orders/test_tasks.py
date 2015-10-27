from django.conf import settings
from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework.test import APITestCase
from orders.models import Refund
from orders.tasks import SendEMailPendingRefundTask
from utils.models import EmailTaskRecord


class SendEmailPendingRefundTaskTest(APITestCase):
    """
    Class to test the task SendEMailPendingRefundTask
    """

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

        self.user = mommy.make(User, first_name='user', email='user@example.com')
        self.refund = mommy.make(Refund, user=self.user)

    def test_send_email(self):
        """
        Test sending email
        """

        task = SendEMailPendingRefundTask()
        task_id = task.delay(self.refund.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.user.email).exists())
