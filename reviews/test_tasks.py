import mock

from django.conf import settings
from model_mommy import mommy
from rest_framework.test import APITestCase

from reviews.models import Review
from reviews.serializers import ReviewSerializer
from reviews.tasks import SendReportReviewEmailTask
from utils.models import EmailTaskRecord


class SendReportReviewEmailTaskTest(APITestCase):
    """
    Class for testing SendReportReviewEmailTask
    """

    def setUp(self):
        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Arrangement
        self.review = mommy.make(Review, rating=3)
        self.email = 'contacto@trulii.com'

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_run(self, send_mail):
        """
        Test the run of the task
        """

        task = SendReportReviewEmailTask()
        task_id = task.delay(review_id=self.review.id)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=self.email, send=True).exists())

        context = {
            'review': ReviewSerializer(self.review).data
        }

        send_mail.assert_called_with(
            'reviews/email/report_review_cc',
            self.email,
            context,
        )
