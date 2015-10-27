from orders.models import Refund
from utils.tasks import SendEmailTaskMixin


class SendEMailPendingRefundTask(SendEmailTaskMixin):
    """
    Task to send an email when the refund get creates
    """

    def run(self, refund_id, *args, **kwargs):
        self.refund = Refund.objects.get(id=refund_id)
        template = 'orders/email/refund_pending_cc'
        return super(SendEMailPendingRefundTask, self).run(instance=self.refund, template=template, **kwargs)

    def get_emails_to(self, *args, **kwargs):
        return [self.refund.user.email]

    def get_context_data(self, data):
        return {
            'name': self.refund.user.first_name,
            'order': self.refund.order.id
        }
