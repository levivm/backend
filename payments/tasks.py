from django.conf import settings

from orders.models import Order
from payments.models import Payment
from utils.tasks import SendEmailTaskMixin


class SendPaymentEmailTask(SendEmailTaskMixin):
    def run(self, order_id, *args, **kwargs):
        self.kwargs = kwargs
        self.order = Order.objects.get(id=order_id)

        if self.order.status == Order.ORDER_APPROVED_STATUS:
            self.template_name = "payments/email/payment_approved.html"
            self.subject = 'Pago Aprobado'
        elif self.order.status == Order.ORDER_DECLINED_STATUS:
            self.template_name = "payments/email/payment_declined.html"
            self.subject = 'Pago Declinado'

        self.emails = [self.order.student.user.email]
        self.global_context = self.get_context_data()
        return super(SendPaymentEmailTask, self).run(*args, **kwargs)

    def get_context_data(self):
        base_url = settings.FRONT_SERVER_URL
        coupon_amount = self.get_coupon_amount()
        card_type = self.get_card_type()

        context_data = {
            'name': self.order.student.user.first_name,
            'activity': self.order.calendar.activity.title,
            'activity_url': base_url + 'activities/%d' % self.order.calendar.activity.id,
            'organizer': self.order.calendar.activity.organizer.name,
            'order_number': self.order.id,
            'buyer': self.order.student.user.get_full_name(),
            'payment_date': self.order.payment.date,
            'status': str(dict(Order.STATUS)[self.order.status]),
            'quantity': self.order.quantity,
            'payment_type': dict(Payment.PAYMENT_TYPE)[self.order.payment.payment_type],
            'card_type': card_type,
            'card_number': self.order.payment.last_four_digits,
            'assistants': [{
                'name': assistant.get_full_name(),
                'email': assistant.email,
                'token': assistant.token,
            } for assistant in self.order.assistants.all()],
            'subtotal': self.order.total_without_coupon,
            'coupon_amount': coupon_amount,
            'total': self.order.total,
            'initial_date': self.order.calendar.initial_date,
            'address': self.order.calendar.activity.location.address,
            'city': self.order.calendar.activity.location.city.name,
            'requirements': self.order.calendar.activity.requirements,
            'detail_url': base_url + 'students/dashboard/history/orders/%s' % self.order.id,
        }

        if not self.order.status == Order.ORDER_APPROVED_STATUS:
            context_data.update({'error': str(self.kwargs.get('transaction_error'))})

        return context_data

    def get_coupon_amount(self):
        amount = None
        if self.order.coupon:
            amount = self.order.coupon.coupon_type.amount

        return amount

    def get_card_type(self):
        if self.order.payment.card_type:
            return dict(Payment.CARD_TYPE)[self.order.payment.card_type]

    def on_success(self, retval, task_id, args, kwargs):
        super(SendPaymentEmailTask, self).on_success(retval, task_id, args, kwargs)

        if not self.order.status == Order.ORDER_APPROVED_STATUS and not \
                        self.order.status == Order.ORDER_PENDING_STATUS:
            self.order.delete()
