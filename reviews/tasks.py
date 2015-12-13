from reviews.models import Review
from utils.tasks import SendEmailTaskMixin
from .serializers import ReviewSerializer


class SendReportReviewEmailTask(SendEmailTaskMixin):
    def run(self, review_id, **kwargs):
        review = Review.objects.get(id=review_id)
        template = "reviews/email/report_review_cc"
        kwargs['review'] = review
        return super().run(instance=review, template=template, **kwargs)

    def get_emails_to(self, *args, **kwargs):
        return ['contacto@trulii.com']

    def get_context_data(self, data):
        review = data.get('review')
        review_data = ReviewSerializer(instance=review).data
        return {
            'review': review_data
        }
