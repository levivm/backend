from model_mommy import mommy
from rest_framework.test import APITestCase

from orders.factories import OrderFactory
from orders.models import Order, Assistant
from referrals.models import Redeem, CouponType
from students.factories import StudentFactory


class OrderModelTest(APITestCase):
    """
    Class for test the model Order
    """

    def setUp(self):
        # Arrangement
        self.student = StudentFactory()
        self.order = OrderFactory(amount=500, student=self.student)

    def test_get_total(self):
        """
        Test method get_total without coupon
        """

        self.assertEqual(self.order.get_total(student=self.student), self.order.amount)

    def test_get_total_with_coupon_not_used(self):
        """
        Test method get_total with a coupon not used
        """

        # Arrangement
        coupon_type = mommy.make(CouponType, name='referred', amount=100)
        redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type=coupon_type)
        self.order.coupon = redeem.coupon
        self.order.save()

        self.assertEqual(self.order.get_total(student=self.student), self.order.amount)

    def test_get_total_with_coupon_used(self):
        """
        Test method get_total with a coupon used
        """

        # Arrangement
        coupon_type = mommy.make(CouponType, name='referred', amount=100)
        redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type=coupon_type,
                            used=True)
        self.order.coupon = redeem.coupon
        self.order.save()
        total = self.order.amount - redeem.coupon.coupon_type.amount

        self.assertEqual(self.order.get_total(student=self.student), total)

    def test_get_total_error(self):
        """
        Test case when total is called without student
        """

        with self.assertRaisesRegex(TypeError, 'get_total().*student'):
            self.order.get_total()


class AssistantModelTest(APITestCase):
    """
    Class test for Assistant
    """

    def setUp(self):
        self.order = OrderFactory(amount=500, status=Order.ORDER_APPROVED_STATUS)
        self.assistants = mommy.make(Assistant, order=self.order, _quantity=2)

    def test_dismiss(self):
        """
        Test dismiss method
        """

        assistant = self.assistants[0]
        assistant.dismiss()

        self.assertFalse(assistant.enrolled)
        self.assertEqual(self.order.status, Order.ORDER_APPROVED_STATUS)

    def test_cancel_order(self):
        """
        Cancel the order if there is not any enrolled assistant
        """

        self.assistants[0].enrolled = False
        self.assistants[0].save()

        assistant = self.assistants[1]
        assistant.dismiss()

        self.assertFalse(assistant.enrolled)
        self.assertEqual(self.order.status, Order.ORDER_CANCELLED_STATUS)
