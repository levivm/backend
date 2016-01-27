from orders.models import Refund
from utils.tasks import SendEmailTaskMixin


class SendEMailStudentRefundTask(SendEmailTaskMixin):
    """
    Task to send an email for the user depending the refund's status
    """

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        self.template_name = 'orders/email/refund_%s_cc_message.txt' % self.refund.status
        self.emails = [self.refund.user.email]
        self.subject = 'Información sobre tu reembolso'
        self.context = self.get_context_data()
        return super(SendEMailStudentRefundTask, self).run(*args, **kwargs)

    def get_context_data(self):
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
        self.template_name = 'orders/email/refund_organizer_cc_message.txt'
        self.emails = [self.refund.order.calendar.activity.organizer.user.email]
        self.subject = 'Reembolso aprobado'
        self.context = self.get_context_data()
        self.global_merge_vars = self.get_global_merge_vars()
        return super(SendEmailOrganizerRefundTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'name': self.refund.order.calendar.activity.organizer.user.first_name,
            'activity': self.refund.order.calendar.activity.title,
            'student': self.refund.user.get_full_name(),
        }
