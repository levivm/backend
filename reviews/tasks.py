from collections import defaultdict

from dateutil.relativedelta import relativedelta, MO
from django.db.models import Max
from django.utils.timezone import now

from activities.models import Calendar
from reviews.models import Review
from utils.tasks import SendEmailTaskMixin


class SendReportReviewEmailTask(SendEmailTaskMixin):
    def run(self, review_id, *args, **kwargs):
        self.review = Review.objects.get(id=review_id)
        self.template_name = "reviews/email/report_review_cc_message.txt"
        self.emails = ['contacto@trulii.com']
        self.subject = 'Denuncia de review!'
        self.global_context = self.get_context_data()
        return super(SendReportReviewEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'id': self.review.id,
            'organizer': self.review.activity.organizer.name,
            'comment': self.review.comment,
            'reply': self.review.reply
        }


class SendCommentToOrganizerEmailTask(SendEmailTaskMixin):
    """
    Send an email to the organizer when a student makes a comment
    in one of his activities
    """

    def run(self, review_id, *args, **kwargs):
        self.review = Review.objects.get(id=review_id)
        self.template_name = "reviews/email/send_comment_to_organizer.html"
        self.emails = [self.review.activity.organizer.user.email]
        self.subject = 'Han comentado una actividad tuya'
        self.global_context = self.get_context_data()
        return super(SendCommentToOrganizerEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
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


class SendReplyToStudentEmailTask(SendEmailTaskMixin):
    """
    Send an email to the student when an organizer makes a reply
    in one of his activities
    """

    def run(self, review_id, *args, **kwargs):
        self.review = Review.objects.get(id=review_id)
        self.template_name = "reviews/email/send_reply_to_student.html"
        self.emails = [self.review.author.user.email]
        self.subject = 'Han respondido a tu comentario'
        self.global_context = self.get_context_data()
        return super(SendReplyToStudentEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'name': self.review.author.user.first_name,
            'organizer': self.review.activity.organizer.name,
            'reply': self.review.reply,
            'url': self.review.get_student_frontend_url(),
        }


class SendReminderReviewEmailTask(SendEmailTaskMixin):
    def run(self, *args, **kwargs):
        self.data = self.get_data()
        if self.data:
            self.emails = self.get_emails()
            self.template_name = 'reviews/email/send_reminder_review.html'
            self.subject = 'Recuerda dejarnos tu review de la actividad'
            self.global_context = {}
            return super(SendReminderReviewEmailTask, self).run(*args, **kwargs)

    def get_data(self):
        last_monday = now() + relativedelta(weekday=MO(-1), hour=0, minute=0)
        last_week_monday = last_monday - relativedelta(weeks=1)
        # calendars = Calendar.objects.all().annotate(last_date=Max('sessions__date'))\
        #     .filter(last_date__isnull=False, last_date__range=(last_week_monday, last_monday))
        # TODO cambiar este filtro si es calendario abierto: se usa la fecha de la orden más un mes
        # - si es cerrado: se usa el intial date del calendario
        calendars = []
        data = defaultdict(list)
        for calendar in calendars:
            students = [o.student for o in calendar.orders.available()
                        if not Review.objects.filter(activity=calendar.activity, author=o.student)]

            for student in students:
                data[student.user.email].append(calendar.activity)

        return data

    def get_emails(self):
        return list(self.data.keys())
