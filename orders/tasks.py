from orders.models import Refund
from utils.tasks import SendEmailTaskMixin


class SendEMailStudentRefundTask(SendEmailTaskMixin):
    """
    Task to send an email for the user depending the refund's status
    """

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        self.template_name = 'orders/email/refund_%s.html' % self.refund_type()
        self.emails = [self.refund.user.email]
        self.subject = 'Información sobre tu reembolso'
        self.global_context = self.get_context_data()
        return super(SendEMailStudentRefundTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'id': self.refund.id,
            'name': self.refund.user.first_name,
            'order': self.refund.order.id,
            'activity': self.refund.order.calendar.activity.title,
            'status': self.refund.get_status_display(),
            'amount': self.refund.amount,
            'assistant': self.refund.assistant.get_full_name() if self.refund.assistant else None,
        }

    def refund_type(self):
        refund_type = 'partial' if self.refund.assistant else 'global'
        return refund_type


class SendEmailOrganizerRefundTask(SendEmailTaskMixin):
    """
    Task to send an email for the organizer depending the refund's status
    """

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        self.template_name = 'orders/email/refund_%s.html' % self.refund_type()
        self.emails = [self.refund.order.calendar.activity.organizer.user.email]
        self.subject = 'Información sobre un reembolso'
        self.global_context = self.get_context_data()
        return super(SendEmailOrganizerRefundTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'id': self.refund.id,
            'name': self.refund.user.first_name,
            'order': self.refund.order.id,
            'activity': self.refund.order.calendar.activity.title,
            'status': self.refund.get_status_display(),
            'amount': self.refund.amount,
            'assistant': self.refund.assistant.get_full_name() if self.refund.assistant else None,
        }

    def refund_type(self):
        refund_type = 'partial' if self.refund.assistant else 'global'
        return refund_type