import mock

from django.conf import settings
from django.template import loader
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
        # Arrangement
        self.review = mommy.make(Review, rating=3)
        self.email = 'contacto@trulii.com'

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        """
        Test the run of the task
        """
        send_mail.return_value = [{
            'email': self.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendReportReviewEmailTask()
        task_id = task.delay(review_id=self.review.id)

        context = {
            'id': self.review.id,
            'organizer': self.review.activity.organizer.name,
            'comment': self.review.comment,
            'reply': self.review.reply
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.email,
            status='sent',
            data=context,
            template_name='reviews/email/report_review_cc_message.txt').exists())
