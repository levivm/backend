from reviews.models import Review
from utils.tasks import SendEmailTaskMixin


class SendReportReviewEmailTask(SendEmailTaskMixin):
    def run(self, review_id, *args, **kwargs):
        self.review = Review.objects.get(id=review_id)
        self.template_name = "reviews/email/report_review_cc_message.txt"
        self.emails = ['contacto@trulii.com']
        self.subject = 'Denuncia de review!'
        self.context = self.get_context_data()
        self.global_merge_vars = self.get_global_merge_vars()
        return super(SendReportReviewEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'id': self.review.id,
            'organizer': self.review.activity.organizer.name,
            'comment': self.review.comment,
            'reply': self.review.reply
        }
