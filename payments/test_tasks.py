import mock
from django.conf import settings
from rest_framework.test import APITestCase

from activities.serializers import CalendarSerializer, ActivitiesSerializer
from orders.factories import OrderFactory, AssistantFactory
from orders.models import Order
from orders.serializers import OrdersSerializer, AssistantsSerializer
from payments.serializers import PaymentSerializer
from payments.tasks import SendPaymentEmailTask
from utils.models import EmailTaskRecord


class SendPaymentEmailTaskTest(APITestCase):
    """
    Class for test SendPaymentEmailTask task
    """

    def get_context_data(self, order):
        return {
            'order': OrdersSerializer(order).data,
            'payment': PaymentSerializer(order.payment).data,
            'calendar': CalendarSerializer(order.calendar).data,
            'activity': ActivitiesSerializer(order.calendar.activity).data,
            'assistants': AssistantsSerializer(order.assistants.all(), many=True, context={'show_token': True}).data,
        }

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_creditcard_order_approved(self, send_mail):
        """
        Test task send the email successfully when the order is approved
        and the payment method is credit card
        """
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS)
        AssistantFactory(order=order)

        context = self.get_context_data(order=order)

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, payment_method=settings.CC_METHOD_PAYMENT_ID)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=order.student.user.email).exists())
        send_mail.assert_called_with(
            'payments/email/payment_approved_cc',
            order.student.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_creditcard_order_declined(self, send_mail):
        """
        Test task send the email successfully when the order is declined
        and the payment method is credit card
        """
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS)
        AssistantFactory(order=order)
        transaction_error = 'ERROR'

        context = self.get_context_data(order=order)
        context['error'] = transaction_error

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, payment_method=settings.CC_METHOD_PAYMENT_ID,
                             transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=order.student.user.email).exists())
        send_mail.assert_called_with(
            'payments/email/payment_declined_cc',
            order.student.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_pse_order_approved(self, send_mail):
        """
        Test task send the email successfully when the order is approved
        and the payment method is PSE
        """
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS)
        AssistantFactory(order=order)

        context = self.get_context_data(order=order)

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, payment_method=settings.PSE_METHOD_PAYMENT_ID)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=order.student.user.email).exists())
        send_mail.assert_called_with(
            'payments/email/payment_approved_pse',
            order.student.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_pse_order_declined(self, send_mail):
        """
        Test task send the email successfully when the order is declined
        and the payment method is pse
        """
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS)
        AssistantFactory(order=order)
        transaction_error = 'ERROR'

        context = self.get_context_data(order=order)
        context['error'] = transaction_error

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, payment_method=settings.PSE_METHOD_PAYMENT_ID,
                             transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=order.student.user.email).exists())
        send_mail.assert_called_with(
            'payments/email/payment_declined_pse',
            order.student.user.email,
            context,
        )

    @mock.patch('users.allauth_adapter.MyAccountAdapter.send_mail')
    def test_send_pse_order_pending(self, send_mail):
        """
        Test task send the email successfully when the order is pending
        and the payment method is pse
        """
        order = OrderFactory(status=Order.ORDER_PENDING_STATUS)
        AssistantFactory(order=order)
        transaction_error = 'Transacción pendiente'

        context = self.get_context_data(order=order)
        context['error'] = transaction_error

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, payment_method=settings.PSE_METHOD_PAYMENT_ID,
                             transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(task_id=task_id, to=order.student.user.email).exists())
        send_mail.assert_called_with(
            'payments/email/payment_pending_pse',
            order.student.user.email,
            context,
        )
