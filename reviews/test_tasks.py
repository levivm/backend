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

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_run(self, send_mail):
        """
        Test the run of the task
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendReportReviewEmailTask()
        task_id = task.delay(review_id=self.review.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.email,
                status='sent').exists())

        context = {
            'id': self.review.id,
            'organizer': self.review.activity.organizer.name,
            'comment': self.review.comment,
            'reply': self.review.reply
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('reviews/email/report_review_cc_message.txt').render(),
            'subject': 'Denuncia de review!',
            'to': [{'email': self.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
