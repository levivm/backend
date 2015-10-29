from orders.models import Refund
from utils.tasks import SendEmailTaskMixin


class SendEMailStudentRefundTask(SendEmailTaskMixin):
    """
    Task to send an email for the user depending the refund's status
    """
    refund = None

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        template = 'orders/email/refund_%s_cc' % self.refund.status
        return super(SendEMailStudentRefundTask, self).run(instance=self.refund, template=template, **kwargs)

    def get_emails_to(self, *args, **kwargs):
        return [self.refund.user.email]

    def get_context_data(self, data):
        return {
            'name': self.refund.user.first_name,
            'order': self.refund.order.id,
            'status': self.refund.status,
        }


class SendEmailOrganizerRefundTask(SendEmailTaskMixin):
    """
    Task to send an email to the organizer when the refund gets approved
    """

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        template = 'orders/email/refund_organizer_cc'
        return super(SendEmailOrganizerRefundTask, self).run(instance=self.refund, template=template, **kwargs)

    def get_emails_to(self, *args, **kwargs):
        return [self.refund.order.calendar.activity.organizer.user.email]

    def get_context_data(self, data):
        return {
            'name': self.refund.order.calendar.activity.organizer.user.first_name,
            'activity': self.refund.order.calendar.activity.title,
            'student': self.refund.user.get_full_name(),
        }