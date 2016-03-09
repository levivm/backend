import mock

from django.conf import settings
from django.template import loader
from model_mommy import mommy
from rest_framework.test import APITestCase

from reviews.factories import ReviewFactory
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from reviews.tasks import SendReportReviewEmailTask, SendCommentToOrganizerEmailTask, \
    SendReplyToStudentEmailTask
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


class SendCommentToOrganizerEmailTaskTest(APITestCase):
    """
    Test the task of SendCommentToOrganizerEmailTask
    """

    def setUp(self):
        self.review = ReviewFactory()

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        send_mail.return_value = [{
            'email': self.review.activity.organizer.user.email,
            'status': 'sent',
            'reject_reason': None,
        }]

        task = SendCommentToOrganizerEmailTask()
        task_id = task.delay(review_id=self.review.id)

        context = {
            'name': self.review.author.user.get_full_name(),
            'activity': {
                'title': self.review.activity.title,
                'url': self.review.activity.get_frontend_url()
            },
            'review': {
                'url': self.review.get_organizer_frontend_url(),
                'comment': self.review.comment,
            }
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.review.activity.organizer.user.email,
            status='sent',
            data=context,
            template_name='reviews/email/send_comment_to_organizer.html').exists())


class SendReplyToStudentEmailTaskTest(APITestCase):
    """
    Test the task of SendCommentToOrganizerEmailTask
    """

    def setUp(self):
        self.review = ReviewFactory()

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        send_mail.return_value = [{
            'email': self.review.author.user.email,
            'status': 'sent',
            'reject_reason': None,
        }]

        task = SendReplyToStudentEmailTask()
        task_id = task.delay(review_id=self.review.id)

        context = {
            'name': self.review.author.user.first_name,
            'organizer': self.review.activity.organizer.name,
            'reply': self.review.reply,
            'url': self.review.get_student_frontend_url(),
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.review.author.user.email,
            status='sent',
            data=context,
            template_name='reviews/email/send_reply_to_student.html').exists())