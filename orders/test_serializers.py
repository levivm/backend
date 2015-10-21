from django.conf import settings
from django.contrib.auth.models import User

from model_mommy import mommy
from rest_framework.exceptions import ValidationError

from rest_framework.test import APITestCase

from activities.models import Calendar
from orders.serializers import OrdersSerializer
from referrals.models import Referral, CouponType, Redeem
from utils.tests import BaseAPITestCase
from orders.models import Order, Assistant, Refund
from orders.serializers import RefundSerializer


class OrdersSerializerTest(BaseAPITestCase):
    """
    Class to test the OrdersSerializer
    """

    def setUp(self):
        super(OrdersSerializerTest, self).setUp()

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Arrangement
        self.referral = mommy.make(Referral, referrer=self.student, referred=self.another_student)
        self.coupon_type = mommy.make(CouponType, name='referrer')
        self.calendar = mommy.make(Calendar, activity__published=True, capacity=10)
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
        class View(object):
            pass

        view = View()
        view.student = self.another_student
        return {
            'view': view,
            'status': Order.ORDER_APPROVED_STATUS,
        }

    def test_create_referrer_coupon(self):
        """
        Test to create a referrer coupon
        """

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
        self.assertTrue(Redeem.objects.filter(student=self.student, coupon__coupon_type=self.coupon_type).exists())


class RefundSerializerTest(APITestCase):
    """
    Class to test the serializer RefundSerializer
    """

    def setUp(self):
        # Arrangement
        self.user = mommy.make(User)
        self.assistant = mommy.make(Assistant)

    def test_read(self):
        """
        Test the serialization of an instance
        """

        # Arrangement
        refund = mommy.make(Refund, user=self.user, order=self.assistant.order, assistant=self.assistant)
        serializer = RefundSerializer(refund)
        content = {
            'id': refund.id,
            'order': self.assistant.order.id,
            'activity': self.assistant.order.calendar.activity.title,
            'created_at': refund.created_at.isoformat()[:-6] + 'Z',
            'amount': self.assistant.order.amount,
            'status': 'pending',
            'assistant': self.assistant.id,
        }

        self.assertEqual(serializer.data, content)

    def test_create(self):
        """
        Test creation of a RefundOrder
        """

        data = {
            'user': self.user.id,
            'assistant': self.assistant.id,
            'order': self.assistant.order.id,
        }

        serializer = RefundSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        content = {
            'id': 1,
            'user_id': self.user.id,
            'assistant_id': self.assistant.id,
            'order_id': self.assistant.order.id,
            'status': 'pending'}

        self.assertTrue(set(content).issubset(instance.__dict__))

    def test_update(self):
        """
        Test update of a RefundOrder
        """

        # Arrangement
        refund = mommy.make(Refund, user=self.user)

        data = {'status': 'approved'}
        serializer = RefundSerializer(refund, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        content = refund.__dict__
        content.update({'status': 'approved'})

        self.assertEqual(refund.id, instance.id)
        self.assertEqual(content, instance.__dict__)

    #
    def test_validation(self):
        """
        Test validation
        """

        data = {
            'user': 1,
            'order': self.assistant.order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        self.assertEqual(Refund.objects.count(), 0)
