# -*- coding: utf-8 -*-
import mock

from django.contrib.auth.models import Permission
from django.db.models import Q
from model_mommy import mommy
from requests.models import Response
from rest_framework import status
from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework.test import APITestCase

from activities.factories import ActivityFactory, CalendarFactory
from activities.models import Calendar
from orders.factories import OrderFactory, AssistantFactory
from orders.models import Order, Assistant
from payments.factories import PaymentFactory
from payments.models import Payment
from referrals.models import Redeem, Referral, Coupon, CouponType
from utils.tests import BaseAPITestCase


class PaymentCreditCardTest(BaseAPITestCase):
    """
    Test cases for the Payment logic
    """

    def setUp(self):
        super(PaymentCreditCardTest, self).setUp()

        self.activity = ActivityFactory(published=True)
        self.calendar = CalendarFactory(activity=self.activity)
        self.url = reverse('orders:create_or_list_by_activity', kwargs={'activity_pk': self.activity.id})

        # Permissions
        permissions = Permission.objects.filter(Q(codename='add_order') | Q(codename='add_assistant'))
        self.student.user.user_permissions.add(*permissions)

    def get_payment_data(self):
        return {
            'token': '32ae9fc3-831b-48bf-876b-e7d8c514c5d2',
            'buyer': {
                'name': 'Ivan Kiehn',
                'email': 'arlington.buckridge@yahoo.com',
            },
            'last_four_digits':'1111',
            'card_association': 'visa',
            'calendar': self.calendar.id,
            'payment_method': Payment.CC_PAYMENT_TYPE,
            'quantity': 1,
            'amount': 324000,
            'assistants': [{
                'first_name': 'Kia',
                'last_name': 'Jakubowski',
                'email': 'camron.schowalter@gmail.com',
            }]
        }

    @mock.patch('activities.utils.post')
    def test_approved(self, payu_post):
        """
        Test when a credit card is approved
        """
        # counters
        payments_counter = Payment.objects.count()
        orders_counter = Order.objects.count()

        # mock the payu response
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'SUCCESS',
            'transactionResponse': {
                'state': 'APPROVED',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()

        # Student should pay
        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), payments_counter + 1)
        self.assertEqual(Order.objects.count(), orders_counter + 1)
        last_order = Order.objects.latest('pk')
        self.assertEqual(last_order.status, 'approved')
        self.assertEqual(last_order.assistants.count(), 1)

    @mock.patch('activities.utils.post')
    def test_declined(self, payu_post):
        """
        Test when a credit card payment is declined
        """

        # Counters
        payments_counter = Payment.objects.count()
        orders_counter = Order.objects.count()

        # mock the payu response
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'SUCCESS',
            'transactionResponse': {
                'state': 'DECLINED',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
                'responseCode': 'INVALID_CARD',
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()

        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(Payment.objects.count(), payments_counter)
        self.assertEqual(Order.objects.count(), orders_counter)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'La tarjeta es inv\xc3\xa1lida', response.content)

    @mock.patch('activities.utils.post')
    def test_pending(self, payu_post):
        """
        Test when a credit card payment is pending
        """

        # Counters
        payments_counter = Payment.objects.count()
        orders_counter = Order.objects.count()

        # mock the payu response
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'SUCCESS',
            'transactionResponse': {
                'state': 'PENDING',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()

        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), payments_counter + 1)
        self.assertEqual(Order.objects.count(), orders_counter + 1)
        last_order = Order.objects.latest('pk')
        self.assertEqual(last_order.status, 'pending')
        self.assertEqual(last_order.assistants.count(), 1)

    @mock.patch('activities.utils.post')
    def test_error(self, payu_post):
        """
        Test when a credit card payment return error
        """

        # Counters
        payments_counter = Payment.objects.count()
        orders_counter = Order.objects.count()

        # mock the payu response
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'ERROR',
            'transactionResponse': {
                'state': 'PENDING',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
                'responseCode': 'ERROR'
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()

        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Payment.objects.count(), payments_counter)
        self.assertEqual(Order.objects.count(), orders_counter)
        self.assertIn(b'ERROR', response.content)


class PayUCreditCardConfirmationTransactionTest(APITestCase):
    """
    Class for testing the responses of PayU web hooks
    """

    def setUp(self):
        self.payu_callback_url = reverse('payments:notification')
        self.payment = PaymentFactory()
        self.order = OrderFactory(payment=self.payment, status=Order.ORDER_PENDING_STATUS)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_transaction_approved(self, send_mail):
        """
        Test the payu response by web hook when is approved
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID

        }
        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        order = Order.objects.get(id=self.order.id)
        self.assertEqual(order.status, Order.ORDER_APPROVED_STATUS)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_transaction_declined(self, send_mail):
        """
        Test the payu response by web hook when is declined
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID

        }

        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=self.order.id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_transaction_expired(self, send_mail):
        """
        Test the payu response by web hook when is expired
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_EXPIRED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID
        }

        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=self.order.id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    def test_payu_confirmation_url_transaction_does_not_exist(self):
        data = {
            'transaction_id': 'invalid_id',
            'state_pol': settings.TRANSACTION_DECLINED_CODE
        }
        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_404_NOT_FOUND)


class PayUPSETest(BaseAPITestCase):

    def setUp(self):
        super(PayUPSETest, self).setUp()
        self.activity = ActivityFactory(published=True)
        self.calendar = CalendarFactory(activity=self.activity)
        self.url = reverse('orders:create_or_list_by_activity', kwargs={'activity_pk': self.activity.id})

        # Permissions
        permissions = Permission.objects.filter(Q(codename='add_order') | Q(codename='add_assistant'))
        self.student.user.user_permissions.add(*permissions)

    def get_payment_data(self):
        return {
            'buyer': {
                'name': 'Deane Shanahan',
                'payerEmail': 'psatterfield@gmail.com',
                 'contactPhone':"037-424-5383"

            },
            'buyer_pse_data':{
                 "response_url": settings.PAYU_RESPONSE_URL,
                 "bank": "1007",
                 "userType": "J",
                 "idType": "NIT",
                 "idNumber": "900823805",
            },
            'calendar': self.calendar.id,
            'activity': self.activity.id,
            'payment_method': Payment.PSE_PAYMENT_TYPE,
            'quantity': 1,
            'amount': 80000,
            'assistants': [{
                'first_name': 'Murphy',
                'last_name': 'Fahey',
                'email': 'bmayert@gmail.com',
            }]
        }

    @mock.patch('activities.utils.post')
    def test_pse_payment(self, payu_post):
        """
        Test the PSE payment when is pending (success)
        """

        # Mock the call to PayU
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'SUCCESS',
            'transactionResponse': {
                'state': 'PENDING',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
                'extraParameters': {
                    'BANK_URL': "https://pse.todo1.com/PseBancolombia/control/\
                                    ElectronicPayment.bancolombia?\
                                    PAYMENT_ID=21429692224921982576571322905"
                }
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()
        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'"bank_url":"https://pse.todo1.com/', response.content)

    @mock.patch('activities.utils.post')
    def test_pse_payment_declined(self, payu_post):
        """
        Test the PSE payment when is declined (fail)
        """

        # Mock the call to PayU
        r = Response()
        r.status_code = 200
        r.json = mock.MagicMock(return_value={
            'code': 'SUCCESS',
            'transactionResponse': {
                'state': 'DECLINED',
                'transactionId': '3e37de3a-1fb3-4f5b-ae99-5f7517ddf81c',
                'responseCode': 'ERROR',
            }
        })
        payu_post.return_value = r

        data = self.get_payment_data()
        response = self.student_client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PayUPSEConfirmationTransactionTest(APITestCase):

    def setUp(self):
        self.payu_callback_url = reverse('payments:notification')
        self.payment = PaymentFactory()
        self.order = OrderFactory(payment=self.payment, status=Order.ORDER_PENDING_STATUS)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_pse_transaction_declined(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'response_code_pol': settings.RESPONSE_CODE_POL_DECLINED,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }

        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_pse_transaction_pending(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_PENDING_PSE_CODE,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        self.assertTrue(Order.objects.filter(id=self.order.id).exists())
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_pse_transaction_failed(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_DECLINED_CODE,
            'response_code_pol': settings.RESPONSE_CODE_POL_FAILED,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        orders = Order.objects.filter(id=self.order.id)
        self.assertEqual(orders.count(), 0)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_payu_confirmation_url_pse_transaction_approved(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID

        }
        payu_callback_response = self.client.post(self.payu_callback_url, data=data)
        order = Order.objects.get(id=self.order.id)
        self.assertEqual(order.status, Order.ORDER_APPROVED_STATUS)
        self.assertEqual(payu_callback_response.status_code, status.HTTP_200_OK)


class PaymentCreditCardWithCouponTest(BaseAPITestCase):
    """
    Test class PaymentUtil
    """

    def setUp(self):
        super(PaymentCreditCardWithCouponTest, self).setUp()

        # Objects
        self.calendar = CalendarFactory(session_price=100000.0, capacity=20, activity__published=True)
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
            'calendar': self.calendar.id,
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
        self.assertTrue(Order.objects.filter(student=self.student, calendar=self.calendar, payment=self.payment,
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
        self.assertTrue(Order.objects.filter(student=self.student, calendar=self.calendar, payment=self.payment,
                                             coupon=self.redeem.coupon, status='pending').exists())
        self.assertFalse(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_declined(self, creditcard):
        """
        Test payment declined with a coupon
        """

        creditcard.return_value = {
            'status': 'DECLINED',
            'payment': self.payment,
            'error': 'Tarjeta inválida',
        }

        # Counter
        order_counter = Order.objects.count()

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        self.assertEqual(Order.objects.count(), order_counter)
        self.assertFalse(Order.objects.filter(coupon=self.redeem.coupon).exists())
        self.assertFalse(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_approved_global_coupon(self, creditcard):
        """
        Test to create a payed order with a global coupon
        """

        # Patch the response of PayU
        creditcard.return_value = {
            'status': 'APPROVED',
            'payment': self.payment
        }

        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        data = {**self.post_data, 'coupon_code': coupon.token}

        response = self.student_client.post(self.create_read_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Order.objects.filter(student=self.student, calendar=self.calendar, payment=self.payment,
                                             coupon=coupon, status='approved').exists())
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_pending_global_coupon(self, creditcard):
        """
        Test pay with coupon and payment pending
        """

        creditcard.return_value = {
            'status': 'PENDING',
            'payment': self.payment,
        }


        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        data = {**self.post_data, 'coupon_code': coupon.token}

        response = self.student_client.post(self.create_read_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Order.objects.filter(student=self.student, calendar=self.calendar, payment=self.payment,
                                             coupon=coupon, status='pending').exists())
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

    @mock.patch('activities.utils.PaymentUtil.creditcard')
    def test_creditcard_declined_global_coupon(self, creditcard):
        """
        Test payment declined with a coupon
        """

        creditcard.return_value = {
            'status': 'DECLINED',
            'payment': self.payment,
            'error': 'Tarjeta inválida',
        }

        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        data = {**self.post_data, 'coupon_code': coupon.token}

        # Counter
        order_counter = Order.objects.count()

        response = self.student_client.post(self.create_read_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.content)
        self.assertEqual(Order.objects.count(), order_counter)
        self.assertFalse(Order.objects.filter(coupon=coupon).exists())
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

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


class PaymentPSEWithCouponTest(BaseAPITestCase):
    """
    Test class PaymentUtil
    """

    def setUp(self):
        super(PaymentPSEWithCouponTest, self).setUp()

        # Objects
        self.calendar = mommy.make(Calendar, session_price=100000.0, capacity=20, activity__published=True)
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
            'buyer': {
                'name': 'PENDING',
                'payerEmail': 'levi@trulii.com',
                'contactPhone': "222222"

            },
            'buyer_pse_data': {
                "response_url": settings.PAYU_RESPONSE_URL,
                "bank": "1007",
                "userType": "J",
                "idType": "NIT",
                "idNumber": "900823805",
            },
            'calendar': self.calendar.id,
            'activity': self.calendar.activity.id,
            'payment_method': Payment.PSE_PAYMENT_TYPE,
            'quantity': 1,
            'amount': 200000,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }],
            'coupon_code': self.redeem.coupon.token,
        }

    @mock.patch('activities.utils.PaymentUtil.pse_payu_payment')
    def test_success(self, pse_payu_payment):
        """
        Test success payment with PSE and a coupon
        """
        # Counter
        order_counter = Order.objects.count()

        # Patch the PayU call
        pse_payu_payment.return_value = {
            'status': 'PENDING',
            'payment': self.payment,
            'bank_url': 'https://pse.todo1.com/',
        }

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'"bank_url":"https://pse.todo1.com/', response.content)
        self.assertEqual(Order.objects.count(), order_counter + 1)
        self.assertTrue(Order.objects.filter(coupon=self.redeem.coupon, status=Order.ORDER_PENDING_STATUS,
                                             calendar=self.calendar, student=self.student,
                                             payment=self.payment).exists())

    @mock.patch('activities.utils.PaymentUtil.pse_payu_payment')
    def test_fail(self, pse_payu_payment):
        """
        Test failed payment with PSE and a coupon
        """
        # Counter
        order_counter = Order.objects.count()

        # Patch the call to PayU
        pse_payu_payment.return_value = {
            'status': 'DECLINED',
            'error': 'The payment was declined',
        }

        response = self.student_client.post(self.create_read_url, self.post_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), order_counter)

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


class PaymentWebHookWithCouponTest(BaseAPITestCase):
    """
    Class to test the payment's web hook with a coupon
    """

    def setUp(self):
        super(PaymentWebHookWithCouponTest, self).setUp()

        # Objects
        self.calendar = CalendarFactory(session_price=100000.0, capacity=20, activity__published=True)
        self.redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type__amount=50000)
        self.payment = mommy.make(Payment, payment_type=Payment.CC_PAYMENT_TYPE)
        self.order = mommy.make(Order, status=Order.ORDER_PENDING_STATUS, payment=self.payment,
                                coupon=self.redeem.coupon, calendar=self.calendar, student=self.student)
        self.assistants = AssistantFactory.create_batch(3, order=self.order)

        self.post_data = self.get_post_data()

        # URLs
        self.payu_callback_url = reverse('payments:notification')

    def get_post_data(self):
        return {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID
        }

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_approved(self, send_mail):
        """
        Test PayU send approved a pending payment
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=self.order.id).status, Order.ORDER_APPROVED_STATUS)
        self.assertTrue(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_decline(self, send_mail):
        """
        Test PayU send declined
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        self.post_data['state_pol'] = settings.TRANSACTION_DECLINED_CODE
        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        self.assertFalse(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_pse_approved(self, send_mail):
        """
        Test approved payment with pse
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        self.payment.payment_type = Payment.PSE_PAYMENT_TYPE
        self.payment.save(update_fields=['payment_type'])
        self.post_data['payment_method_type'] = settings.PSE_METHOD_PAYMENT_ID

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=self.order.id).status, Order.ORDER_APPROVED_STATUS)
        self.assertTrue(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_pse_decline(self, send_mail):
        """
        Test PayU send declined
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        self.payment.payment_type = Payment.PSE_PAYMENT_TYPE
        self.payment.save(update_fields=['payment_type'])
        self.post_data['payment_method_type'] = settings.PSE_METHOD_PAYMENT_ID
        self.post_data['state_pol'] = settings.TRANSACTION_DECLINED_CODE
        self.post_data['response_code_pol'] = settings.RESPONSE_CODE_POL_DECLINED

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        self.assertFalse(Redeem.objects.get(id=self.redeem.id).used)

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_approved_global_coupon(self, send_mail):
        """
        Test PayU send approved a pending payment with a global coupon
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]


        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        self.order.coupon = coupon
        self.order.save()

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=self.order.id).status, Order.ORDER_APPROVED_STATUS)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_decline_global_coupon(self, send_mail):
        """
        Test PayU send declined with global coupon
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]


        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        self.order.coupon = coupon
        self.order.save()
        self.post_data['state_pol'] = settings.TRANSACTION_DECLINED_CODE

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

    def test_pse_approved_global_coupon(self):
        """
        Test approved payment with pse
        """
        self.payment.payment_type = Payment.PSE_PAYMENT_TYPE
        self.payment.save(update_fields=['payment_type'])
        self.post_data['payment_method_type'] = settings.PSE_METHOD_PAYMENT_ID

        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        self.order.coupon = coupon
        self.order.save()

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.get(id=self.order.id).status, Order.ORDER_APPROVED_STATUS)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_pse_decline_global_coupon(self, send_mail):
        """
        Test PayU send declined with global coupon
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.order.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        self.payment.payment_type = Payment.PSE_PAYMENT_TYPE
        self.payment.save(update_fields=['payment_type'])
        self.post_data['payment_method_type'] = settings.PSE_METHOD_PAYMENT_ID
        self.post_data['state_pol'] = settings.TRANSACTION_DECLINED_CODE
        self.post_data['response_code_pol'] = settings.RESPONSE_CODE_POL_DECLINED

        coupon = mommy.make(Coupon, coupon_type__type='global', coupon_type__amount=100000)
        self.order.coupon = coupon
        self.order.save()

        response = self.client.post(self.payu_callback_url, self.post_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Order.objects.filter(id=self.order.id).exists())
        self.assertFalse(Redeem.objects.filter(student=self.student, coupon=coupon, used=True).exists())


class PaymentWebHookTest(BaseAPITestCase):
    """
    Class to test the payment webhook for PayU
    """

    def setUp(self):
        super(PaymentWebHookTest, self).setUp()

        # Arrangement
        self.calendar = CalendarFactory(activity__published=True, capacity=10)
        self.payment = mommy.make(Payment, payment_type=Payment.CC_PAYMENT_TYPE)
        self.order = mommy.make(Order, calendar=self.calendar, student=self.another_student, payment=self.payment)
        self.referral = mommy.make(Referral, referrer=self.student, referred=self.another_student)
        self.coupon_type = mommy.make(CouponType, name='referrer')

        # URLs
        self.payu_callback_url = reverse('payments:notification')

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

    def test_cc_create_referrer_coupon(self):
        """
        Test should create a referrer coupon
        """

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.CC_METHOD_PAYMENT_ID
        }

        response = self.client.post(self.payu_callback_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Coupon.objects.count(), coupon_counter + 1)
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())

    def test_pse_create_referrer_coupon(self):
        """
        Test should create a referrer coupon
        """

        # Counter
        coupon_counter = Coupon.objects.count()
        redeem_counter = Redeem.objects.count()

        data = {
            'transaction_id': self.payment.transaction_id,
            'state_pol': settings.TRANSACTION_APPROVED_CODE,
            'payment_method_type': settings.PSE_METHOD_PAYMENT_ID
        }

        response = self.client.post(self.payu_callback_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Coupon.objects.count(), coupon_counter + 1)
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())
