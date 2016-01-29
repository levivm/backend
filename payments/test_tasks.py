import mock
from django.conf import settings
from django.template import loader
from rest_framework.test import APITestCase

from orders.factories import OrderFactory, AssistantFactory
from orders.models import Order
from payments.factories import PaymentFactory
from payments.models import Payment
from payments.tasks import SendPaymentEmailTask
from referrals.factories import RedeemFactory
from students.factories import StudentFactory
from utils.models import EmailTaskRecord
from utils.tests import TestMixinUtils


class SendPaymentEmailTaskTest(TestMixinUtils, APITestCase):
    """
    Class for test SendPaymentEmailTask task
    """

    def setUp(self):
        self.base_url = settings.FRONT_SERVER_URL

    def get_context_data(self, order, assistants):
        payment = order.payment
        return {
            'name': order.student.user.first_name,
            'activity': order.calendar.activity.title,
            'activity_url': self.base_url + 'activities/%d' % order.calendar.activity.id,
            'order_number': order.id,
            'buyer': order.student.user.get_full_name(),
            'payment_date': order.payment.date.strftime('%-d %b %Y'),
            'quantity': order.quantity,
            'card_number': str(payment.last_four_digits),
            'assistants': [{
                               'name': assistant.get_full_name(),
                               'email': assistant.email,
                               'token': assistant.token,
                           } for assistant in assistants],
            'subtotal': order.total_without_coupon,
            'total': order.total,
            'initial_date': order.calendar.initial_date.strftime('%A %-d de %B a las %-I:%M %p'),
            'address': order.calendar.activity.location.address,
            'requirements': order.calendar.activity.requirements,
            'detail_url': self.base_url + '/students/dashboard/history/orders/%s' % order.id,
        }

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_creditcard_with_coupon_order_approved(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is approved
        - the payment method is credit card
        - the order has a coupon
        """

        student = StudentFactory()
        redeem = RedeemFactory(student=student, used=True)
        payment = PaymentFactory(payment_type='CC', card_type='visa')
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS, payment=payment,
                             student=student, coupon=redeem.coupon)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Aprobada',
            'payment_type': 'Crédito',
            'card_type': 'VISA',
            'coupon_amount': redeem.coupon.coupon_type.amount,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_approved_cc_message.txt').render(),
            'subject': 'Pago Aprobado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_creditcard_without_coupon_order_approved(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is approved
        - the payment method is credit card
        - the order doesn't have a coupon
        """

        payment = PaymentFactory(payment_type='CC', card_type='visa')
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS, payment=payment)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Aprobada',
            'payment_type': 'Crédito',
            'card_type': 'VISA',
            'coupon_amount': None,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_approved_cc_message.txt').render(),
            'subject': 'Pago Aprobado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_creditcard_order_with_coupon_declined(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is declined
        - the payment method is credit card
        - the order has a coupon
        """

        student = StudentFactory()
        redeem = RedeemFactory(student=student, used=True)
        payment = PaymentFactory(payment_type='CC', card_type='visa')
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS, payment=payment,
                             student=student, coupon=redeem.coupon)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)
        transaction_error = 'ERROR'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Declinada',
            'payment_type': 'Crédito',
            'card_type': 'VISA',
            'coupon_amount': redeem.coupon.coupon_type.amount,
            'error': transaction_error,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_declined_cc_message.txt').render(),
            'subject': 'Pago Declinado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_creditcard_order_without_coupon_declined(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is declined
        - the payment method is credit card
        - the order doesn't have a coupon
        """

        payment = PaymentFactory(payment_type='CC', card_type='visa')
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS, payment=payment)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)
        transaction_error = 'ERROR'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Declinada',
            'payment_type': 'Crédito',
            'card_type': 'VISA',
            'coupon_amount': None,
            'error': transaction_error,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_declined_cc_message.txt').render(),
            'subject': 'Pago Declinado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_pse_with_coupon_order_approved(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is approved
        - the payment method is pse
        - the order has a coupon
        """

        student = StudentFactory()
        redeem = RedeemFactory(student=student, used=True)
        payment = PaymentFactory(payment_type='PSE')
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS, payment=payment,
                             student=student, coupon=redeem.coupon)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Aprobada',
            'payment_type': 'PSE',
            'card_type': dict(Payment.CARD_TYPE)[payment.card_type],
            'coupon_amount': redeem.coupon.coupon_type.amount,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_approved_cc_message.txt').render(),
            'subject': 'Pago Aprobado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_pse_without_coupon_order_approved(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is approved
        - the payment method is pse
        - the order doesn't have a coupon
        """

        payment = PaymentFactory(payment_type='PSE')
        order = OrderFactory(status=Order.ORDER_APPROVED_STATUS, payment=payment)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Aprobada',
            'payment_type': 'PSE',
            'card_type': dict(Payment.CARD_TYPE)[payment.card_type],
            'coupon_amount': None,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_approved_cc_message.txt').render(),
            'subject': 'Pago Aprobado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_pse_order_with_coupon_declined(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is declined
        - the payment method is pse
        - the order has a coupon
        """

        student = StudentFactory()
        redeem = RedeemFactory(student=student, used=True)
        payment = PaymentFactory(payment_type='PSE')
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS, payment=payment,
                             student=student, coupon=redeem.coupon)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)
        transaction_error = 'ERROR'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Declinada',
            'payment_type': 'PSE',
            'card_type': dict(Payment.CARD_TYPE)[payment.card_type],
            'coupon_amount': redeem.coupon.coupon_type.amount,
            'error': transaction_error,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_declined_cc_message.txt').render(),
            'subject': 'Pago Declinado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_send_pse_order_without_coupon_declined(self, send_mail):
        """
        Test task send the email successfully when:
        - the order is declined
        - the payment method is pse
        - the order doesn't have a coupon
        """

        payment = PaymentFactory(payment_type='PSE')
        order = OrderFactory(status=Order.ORDER_DECLINED_STATUS, payment=payment)
        email = order.student.user.email
        assistants = AssistantFactory.create_batch(1, order=order)
        transaction_error = 'ERROR'

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendPaymentEmailTask()
        task_id = task.delay(order.id, transaction_error=transaction_error)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=email,
            status='sent').exists())

        context = {
            **self.get_context_data(order, assistants),
            'status': 'Declinada',
            'payment_type': 'PSE',
            'card_type': dict(Payment.CARD_TYPE)[payment.card_type],
            'coupon_amount': None,
            'error': transaction_error,
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('payments/email/payment_declined_cc_message.txt').render(),
            'subject': 'Pago Declinado',
            'to': [{'email': email}],
            'merge_vars': [],
        }

        global_merge_vars = [{'name': k, 'content': v} for k, v in context.items()]
        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
        self.assertTrue(
            all(item in called_message['global_merge_vars'] for item in global_merge_vars))
