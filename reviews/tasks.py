from reviews.models import Review
from utils.tasks import SendEmailTaskMixin


class SendReportReviewEmailTask(SendEmailTaskMixin):
    def run(self, review_id, template, **kwargs):
        review = Review.objects.get(id=review_id)
        template = "reviews/email/report_review_cc"
        kwargs['review'] = review
        return super().run(instance=review, template=template, **kwargs)

    def get_emails_to(self, **kwargs):
        return ['contacto@trulii.com']

    def get_context_data(self, data):
        review = data.get('review')
        return {
            'review': review
        }
