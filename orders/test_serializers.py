from mock import Mock
from django.conf import settings
from django.contrib.auth.models import User
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.models import Calendar
from orders.serializers import OrdersSerializer
from organizers.models import Organizer
from payments.models import Fee
from referrals.models import Referral, CouponType, Redeem
from students.models import Student
from utils.models import EmailTaskRecord
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
        view = Mock(student=self.another_student)
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

    def test_validate_quantity(self):
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
        calendar = mommy.make(Calendar, activity__published=True, is_free=True, capacity=10)
        self.data['calendar'] = calendar.id

        serializer = OrdersSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        self.assertIsNone(order.fee)

    def test_fee(self):
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


class RefundSerializerTest(APITestCase):
    """
    Class to test the serializer RefundSerializer
    """

    def setUp(self):
        # Arrangement
        self.user = mommy.make(User)
        self.order = mommy.make(Order, amount=500, quantity=1)
        self.assistant = mommy.make(Assistant, order=self.order)

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

    def test_read(self):
        """
        Test the serialization of an instance
        """

        # Arrangement
        refund = mommy.make(Refund, user=self.user, order=self.order, assistant=self.assistant)
        serializer = RefundSerializer(refund)
        content = {
            'id': refund.id,
            'order': self.order.id,
            'activity': self.order.calendar.activity.title,
            'created_at': refund.created_at.isoformat()[:-6] + 'Z',
            'amount': self.order.amount / self.order.quantity,
            'status': 'Pendiente',
            'assistant': self.assistant.id,
        }

        self.assertEqual(serializer.data, content)

    def test_create(self):
        """
        Test creation of a Refund
        """

        # Counter
        email_task_record_counter = EmailTaskRecord.objects.count()

        # Arrangement
        data = {
            'user': self.user.id,
            'assistant': self.assistant.id,
            'order': self.order.id,
            'status': 'approved',
        }

        serializer = RefundSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        content = {
            'user_id': self.user.id,
            'assistant_id': self.assistant.id,
            'order_id': self.order.id,
            'status': 'pending'}


        self.assertTrue(all(item in instance.__dict__.items() for item in content.items()))
        self.assertEqual(EmailTaskRecord.objects.count(), email_task_record_counter + 1)

    def test_create_assistant_validation(self):
        """
        Test assistant validation when create a Refund
        Raise validation error if the assistant doesn't belong to the order
        """

        data = {
            'user': self.user.id,
            'assistant': mommy.make(Assistant).id,
            'order': self.order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_create_duplicated(self):
        """
        Test duplication of a Refund
        """

        mommy.make(Refund, assistant=self.assistant, order=self.order, user=self.user)
        data = {
            'user': self.user.id,
            'assistant': self.assistant.id,
            'order': self.order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_update(self):
        """
        Test update of a Refund
        """

        # Counter
        email_task_record_counter = EmailTaskRecord.objects.count()

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
        self.assertEqual(EmailTaskRecord.objects.count(), email_task_record_counter)

    def test_user_validation(self):
        """
        Test validation
        """

        data = {
            'user': 1,
            'order': self.order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        self.assertEqual(Refund.objects.count(), 0)

    def test_create_type_validation(self):
        """
        Test to validate if exists an order refund doesn't allow to create
        an assistant refund for that order and backwards
        """

        refund = mommy.make(Refund, user=self.user, order=self.order)
        data = {
            'user': self.user.id,
            'order': self.order.id,
            'assistant': self.assistant.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

        # Backwards
        refund.assistant = self.assistant
        refund.save()

        del data['assistant']

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_order_belongs_student_validation(self):
        """
        Test to validate if the order belongs to the student
        """

        mommy.make(Student, user=self.user)
        order = mommy.make(Order)
        data = {
            'user': self.user.id,
            'order': order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)

    def test_order_related_organizer_validation(self):
        """
        Test to validate if the order is related with an organizer's activity
        """

        mommy.make(Organizer, user=self.user)
        order = mommy.make(Order)
        data = {
            'user': self.user.id,
            'order': order.id,
        }

        with self.assertRaises(ValidationError):
            serializer = RefundSerializer(data=data)
            serializer.is_valid(raise_exception=True)
