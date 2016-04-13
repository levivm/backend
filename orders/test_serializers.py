import mock
from mock import Mock
from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from activities.models import Calendar
from orders.models import Order, Assistant
from orders.serializers import OrdersSerializer, AssistantsSerializer
from payments.models import Fee, Payment
from payments.serializers import PaymentSerializer
from referrals.models import Referral, CouponType, Redeem
from students.serializer import StudentsSerializer
from utils.serializers import UnixEpochDateField
from utils.tests import BaseAPITestCase


class OrdersSerializerTest(BaseAPITestCase):
    """
    Class to test the OrdersSerializer
    """

    def setUp(self):
        super(OrdersSerializerTest, self).setUp()

        # Arrangement
        self.referral = mommy.make(Referral, referrer=self.student, referred=self.another_student)
        self.coupon_type = mommy.make(CouponType, name='referrer')
        self.calendar = mommy.make(Calendar, activity__published=True, available_capacity=10)
        self.data = self.get_data()
        self.context = self.get_context()

    def get_data(self):
        return {
            'calendar': self.calendar.id,
            'quantity': 1,
            'amount': 500,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }

    def get_context(self):
        view = Mock(student=self.another_student)
        return {
            'view': view,
            'status': Order.ORDER_APPROVED_STATUS,
        }

    def test_read(self):
        """
        Test data serialized
        """

        payment = mommy.make(Payment)
        fee = mommy.make(Fee)
        order = mommy.make(Order, coupon__coupon_type=self.coupon_type, calendar=self.calendar,
                           quantity=1, amount=500,
                           payment=payment, fee=fee)
        assistants = mommy.make(Assistant, order=order, _quantity=1)
        serializer = OrdersSerializer(order)

        content = {
            'id': order.id,
            'calendar': self.calendar.id,
            'student': StudentsSerializer(order.student).data,
            'quantity': order.quantity,
            'assistants': AssistantsSerializer(assistants, many=True).data,
            'amount': order.amount,
            'status': order.get_status_display(),
            'created_at': UnixEpochDateField().to_representation(order.created_at),
            'payment': PaymentSerializer(payment).data,
            'calendar_initial_date': UnixEpochDateField().to_representation(
                order.calendar.initial_date),
            'activity_id': order.calendar.activity.id,
            'fee': fee.amount,
            'is_free': order.is_free,
            'total': order.total,
            'coupon': {
                'amount': self.coupon_type.amount,
                'code': order.coupon.token,
            },
        }

        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_create_referrer_coupon(self, delay):
        """
        Test to create a referrer coupon
        """
        delay.return_value = None

        # Counter
        order_counter = Order.objects.count()
        redeem_counter = Redeem.objects.count()

        serializer = OrdersSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(Order.objects.count(), order_counter + 1)
        self.assertTrue(Order.objects.filter(student=self.another_student).exists())
        self.assertEqual(Redeem.objects.count(), redeem_counter + 1)
        self.assertTrue(Redeem.objects.filter(student=self.student,
                                              coupon__coupon_type=self.coupon_type).exists())

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_validate_quantity(self, delay):
        """
        Test to validate quantity with the number of assistants
        """

        # Success
        serializer = OrdersSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        self.assertEqual(self.data['quantity'], order.quantity)
        self.assertEqual(order.quantity, order.assistants.count())

        # ValidationError
        self.data['quantity'] = 4
        serializer = OrdersSerializer(data=self.data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_free_activity_fee(self):
        """
        Test no fee in the order because is a free activity
        """

        # Arrangement
        calendar = mommy.make(Calendar, activity__published=True, is_free=True, available_capacity=10)
        self.data['calendar'] = calendar.id

        serializer = OrdersSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        self.assertIsNone(order.fee)

    @mock.patch('referrals.tasks.SendCouponEmailTask.delay')
    def test_fee(self, delay):
        """
        Test fee on the order
        """
        # Arrangement
        fee = mommy.make(Fee, amount=0.08)

        serializer = OrdersSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        self.assertEqual(order.fee, fee)
