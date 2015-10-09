import json

import mock
from django.contrib.auth.models import Permission
from model_mommy import mommy
from rest_framework import status
from django.core.urlresolvers import reverse
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from activities.models import Chronogram
from orders.models import Order
from orders.views import OrdersViewSet
from payments.models import Payment
from referrals.models import Redeem
from utils.tests import BaseViewTest, BaseAPITestCase
from .tasks import SendPaymentEmailTask
from utils.models import EmailTaskRecord
from activities.utils import PaymentUtil


class PaymentLogicTest(BaseViewTest):
    url = '/api/activities/1/orders'
    payu_callback_url = '/api/payments/notification/'
    view = OrdersViewSet
    ORDER_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def get_payments_count(self):
        return Payment.objects.count()

    def get_orders_count(self):
        return Order.objects.count()

    def test_payu_confirmation_url_transaction_does_not_exist(self):
        client = self.get_student_client()
        data = {
            'transaction_id': 'invalid_id',
            'state_pol': settings.TRANSACTION_DECLINED_CODE
        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_payu_confirmation_url_transaction_expired(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_EXPIRED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID
        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_transaction_declined(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_transaction_approved(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.ORDER_APPROVED_STATUS)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_creditcard_declined(self):
        payments_count = self.get_payments_count()
        orders_count = self.get_orders_count()
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'DECLINED'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(self.get_payments_count(), payments_count)
        self.assertEqual(self.get_orders_count(), orders_count)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'Su tarjeta ha sido rechazada', response.content)

    def test_creditcard_approved(self):
        payments_count = self.get_payments_count()
        orders_count = self.get_orders_count()
        client = self.get_student_client()
        response = client.post(self.url, json.dumps(self.get_payment_data()), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_payments_count(), payments_count + 1)
        self.assertEqual(self.get_orders_count(), orders_count + 1)
        last_order = Order.objects.latest('pk')
        self.assertEqual(last_order.status, 'approved')
        self.assertEqual(last_order.assistants.count(), 1)

    def test_creditcard_pending(self):
        payments_count = self.get_payments_count()
        orders_count = self.get_orders_count()
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.get_payments_count(), payments_count + 1)
        self.assertEqual(self.get_orders_count(), orders_count + 1)
        last_order = Order.objects.latest('pk')
        self.assertEqual(last_order.status, 'pending')
        self.assertEqual(last_order.assistants.count(), 1)

    def test_creditcard_error(self):
        payments_count = self.get_payments_count()
        orders_count = self.get_orders_count()
        client = self.get_student_client()
        data = self.get_payment_data()
        data['token'] = '1234567890'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.get_payments_count(), payments_count)
        self.assertEqual(self.get_orders_count(), orders_count)
        self.assertIn(b'ERROR', response.content)

    def test_payment_approved_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_APPROVED_STATUS)
        task = SendPaymentEmailTask()
        task_data = {
            'payment_method': settings.CC_METHOD_PAYMENT_ID
        }
        result = task.apply_async((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])
        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 1)

    def test_payu_declined_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_DECLINED_STATUS)
        error_msg = PaymentUtil.RESPONSE_CODE_NOTIFICATION_URL \
            .get('ENTITY_DECLINED', 'Error')
        task_data = {
            'transaction_error': error_msg,
            'payment_method': settings.CC_METHOD_PAYMENT_ID

        }
        task = SendPaymentEmailTask()
        result = task.apply((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
        expected_error = str(error_msg)
        self.assertEqual(expected_error, email_task.data['error'])
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])

        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 0)


class PayUPSETest(BaseViewTest):
    # url = '/api/payments/pse'
    url = '/api/activities/1/orders'
    payu_callback_url = '/api/payments/notification/'
    ORDER_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def get_payments_count(self):
        return Payment.objects.count()

    def get_orders_count(self):
        return Order.objects.count()

    def test_pse_payment(self):
        client = self.get_student_client()
        data = json.dumps(self.get_payment_pse_data())
        response = client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'"bank_url":"https://pse.todo1.com/', response.content)

    def test_pse_payment_declined(self):
        client = self.get_student_client()
        data = self.get_payment_pse_data()
        data['buyer']['name'] = 'DECLINED'
        data = json.dumps(data)
        response = client.post(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payu_confirmation_url_pse_transaction_declined(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data),
                               content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'response_code_pol': settings.RESPONSE_CODE_POL_DECLINED,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_pse_transaction_pending(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_PENDING_PSE_CODE,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(), 1)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_pse_transaction_failed(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'response_code_pol': settings.RESPONSE_CODE_POL_FAILED,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_pse_transaction_approved(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = int(response.data['id'])
        order = Order.objects.get(id=order_id)
        payment = Payment.objects.get(order=order)
        data = {
            'transaction_id': payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = client.post(self.payu_callback_url, data=data)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status, Order.ORDER_APPROVED_STATUS)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payment_pse_approved_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_APPROVED_STATUS)
        task = SendPaymentEmailTask()
        task_data = {
            'payment_method': settings.PSE_METHOD_PAYMENT_ID
        }
        result = task.apply_async((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])
        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 1)

    def test_payment_pse_declined_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_DECLINED_STATUS)
        error_msg = _('Transacción Rechazada')
        task_data = {
            'transaction_error': error_msg,
            'payment_method': settings.PSE_METHOD_PAYMENT_ID

        }
        task = SendPaymentEmailTask()
        result = task.apply((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        expected_error = str(error_msg)
        self.assertTrue(email_task.send)
        self.assertEqual(expected_error, email_task.data['error'])
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])

        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 0)

    def test_payment_pse_failed_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_DECLINED_STATUS)
        error_msg = _('Transacción Fallida')
        task_data = {
            'transaction_error': error_msg,
            'payment_method': settings.PSE_METHOD_PAYMENT_ID

        }
        task = SendPaymentEmailTask()
        result = task.apply((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        expected_error = str(error_msg)
        self.assertEqual(expected_error, email_task.data['error'])
        self.assertTrue(email_task.send)
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])
        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 0)

    def test_payment_pse_pending_notification_email_task(self):
        order = Order.objects.get(id=self.ORDER_ID)
        order.change_status(Order.ORDER_PENDING_STATUS)
        error_msg = 'Transacción pendiente, por favor revisar'
        error_msg += 'si el débito fue realizado en el banco.'
        error_msg = _(error_msg)
        task_data = {
            'transaction_error': error_msg,
            'payment_method': settings.PSE_METHOD_PAYMENT_ID

        }
        task = SendPaymentEmailTask()
        result = task.apply((order.id,), task_data, countdown=4)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
        expected_error = str(error_msg)
        self.assertEqual(expected_error, email_task.data['error'])
        self.assertEqual(self.ORDER_ID, email_task.data['order']['id'])
        orders = Order.objects.filter(id=self.ORDER_ID)
        self.assertEqual(orders.count(), 1)

        # class PaymentBankListTest(BaseViewTest):


# url = '/api/payments/pse/banks'

#     def test_get_pse_bank_list(self):
#         client = self.get_student_client()
#         response = client.get(self.url)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIn(b'"description":"BANCOLOMBIA QA"', response.content)


class PaymentWithCouponTest(BaseAPITestCase):
    """
    Test class PaymentUtil
    """

    def setUp(self):
        super(PaymentWithCouponTest, self).setUp()

        # Objects
        self.calendar = mommy.make(Chronogram, session_price=100000.0, capacity=20, activity__published=True)
        self.redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type__amount=50000)
        self.payment = mommy.make(Payment)
        self.post_data = self.get_post_data()

        # URLs
        self.create_read_url = reverse('orders:create_or_list_by_activity',
                                       kwargs={'activity_pk': self.calendar.activity.id})

        # Set permissions
        permission = Permission.objects.get_by_natural_key('add_order', 'orders', 'order')
        permission.user_set.add(self.student.user)
        permission.user_set.add(self.another_student.user)


    def get_post_data(self):
        return {
            'chronogram': self.calendar.id,
            'quantity': 1,
            'payment_method': Payment.CC_PAYMENT_TYPE,
            'card_association': 'visa',
            'last_four_digits': '1111',
            'buyer': {
                'name': 'APPROVED',
                'email': 'test@payulatam.com',
            },
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }],
            'token': '098adf-ads983498adsf-39843',
            'coupon_code': self.redeem.coupon.token,
        }

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_approved(self, creditcard):
        """
        Test to create (and pay) an order with a coupon
        """

        # Patch the response of PayU
        creditcard.return_value = {
            'status': 'APPROVED',
            'payment': self.payment
        }

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Order.objects.filter(student=self.student, chronogram=self.calendar, payment=self.payment,
                                             coupon=self.redeem.coupon, status='approved').exists())
        self.assertTrue(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_pending(self, creditcard):
        """
        Test pay with coupon and payment pending
        """

        creditcard.return_value = {
            'status': 'PENDING',
            'payment': self.payment,
        }

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Order.objects.filter(student=self.student, chronogram=self.calendar, payment=self.payment,
                                             coupon=self.redeem.coupon, status='pending').exists())
        self.assertFalse(Redeem.objects.get(id=self.redeem.id).used)

    def test_creditcard_non_existent_coupon(self):
        """
        Test payment with non-existent coupon
        """

        # Non-existent coupon
        self.post_data['coupon_code'] = 'REFERRAL-INVALID'

        # Counter
        order_counter = Order.objects.count()

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Order.objects.count(), order_counter)

    def test_creditcard_invalid_coupon(self):
        """
        Test payment with invalid coupon
        """

        # Counter
        order_counter = Order.objects.count()

        # Another_student doesn't have a coupon
        response = self.another_student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), order_counter)

        # Student already used the coupon
        self.redeem.used = True
        self.redeem.save(update_fields=['used'])

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), order_counter)
