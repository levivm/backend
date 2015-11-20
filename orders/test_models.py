from django.db.utils import IntegrityError
from model_mommy import mommy
from rest_framework.test import APITestCase

from orders.models import Order, Refund, Assistant
from referrals.models import Redeem, CouponType, Coupon


class OrderModelTest(APITestCase):
    """
    Class for test the model Order
    """

    def setUp(self):
        # Arrangement
        self.student = mommy.make_recipe('students.student')
        self.order = mommy.make(Order, amount=500, student=self.student)

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
        redeem = mommy.make(Redeem, student=self.student, coupon__coupon_type=coupon_type, used=True)
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
        self.order = mommy.make(Order, amount=500, status=Order.ORDER_APPROVED_STATUS)
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

class RefundModelTest(APITestCase):
    """
    Class for testing the model Refund
    """
    ASSISTANT_QUANTITY = 2
    ORDER_AMOUNT = 500.0
    COUPON_AMOUNT = 100

    ORDER_AMOUNT_WITHOUT_COUPON = ORDER_AMOUNT
    ORDER_AMOUNT_WITH_COUPON = ORDER_AMOUNT - COUPON_AMOUNT

    ASSISTANT_AMOUNT_WITHOUT_COUPON = ORDER_AMOUNT / ASSISTANT_QUANTITY
    ASSISTANT_AMOUNT_WITH_COUPON = (ORDER_AMOUNT - COUPON_AMOUNT) / ASSISTANT_QUANTITY

    def setUp(self):
        # Arrangement
        self.organizer = mommy.make_recipe('organizers.organizer')
        self.student = mommy.make_recipe('students.student')
        self.coupon = mommy.make(Coupon, coupon_type__amount=self.COUPON_AMOUNT)
        self.redeem = mommy.make(Redeem, student=self.student, used=True, coupon=self.coupon)
        self.order = mommy.make(Order, quantity=self.ASSISTANT_QUANTITY, amount=self.ORDER_AMOUNT,
                                coupon=self.coupon, student=self.student)
        self.assistants = mommy.make(Assistant, _quantity=self.ASSISTANT_QUANTITY, order=self.order)

    def test_create_duplicated(self):
        """
        Test duplication of a Refund
        """

        data = {
            'user': self.student.user,
            'assistant': self.assistants[0],
            'order': self.order,
        }

        Refund.objects.create(**data)
        with self.assertRaises(IntegrityError):
            Refund.objects.create(**data)

    def test_amount_order(self):
        """
        Test the amount's property for order's refund
        """

        # Order without coupon
        self.order.coupon = None
        self.order.save()

        # Organizer
        refund = mommy.make(Refund, user=self.organizer.user, order=self.order)
        self.assertEqual(refund.amount, self.ORDER_AMOUNT_WITHOUT_COUPON)

        # Student
        refund = mommy.make(Refund, user=self.student.user, order=self.order)
        self.assertEqual(refund.amount, self.ORDER_AMOUNT_WITHOUT_COUPON)

    def test_amount_order_with_used_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Order with student's used coupon
        """

        # Student
        refund = mommy.make(Refund, user=self.student.user, order=self.order)
        self.assertEqual(refund.amount, self.ORDER_AMOUNT_WITH_COUPON)

    def test_amount_order_with_unused_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Order with student's unused coupon
        """

        # Student
        self.redeem.used = False
        self.redeem.save()
        refund = mommy.make(Refund, user=self.student.user, order=self.order)
        self.assertEqual(refund.amount, self.ORDER_AMOUNT_WITHOUT_COUPON)

    def test_amount_order_with_another_students_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Order with other student's coupon
        """

        # Another student has a redeem with the same coupon
        another_student = mommy.make_recipe('students.student')
        mommy.make(Redeem, student=another_student, used=True, coupon=self.coupon)

        # The student doesn't have a redeem
        self.redeem.delete()

        refund = mommy.make(Refund, user=self.student.user, order=self.order)
        self.assertEqual(refund.amount, self.ORDER_AMOUNT_WITHOUT_COUPON)

    def test_amount_assistant_organizer(self):
        """
        Test amount's property for an assistant's refund
        """

        # Order without coupon
        self.order.coupon = None
        self.order.save()

        # Organizer
        refund = mommy.make(Refund, user=self.organizer.user, order=self.order, assistant=self.assistants[0])
        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITHOUT_COUPON)

    def test_amount_assistant_student(self):
        """
        Test amount's property for an assistant's refund
        """

        # Order without coupon
        self.order.coupon = None
        self.order.save()

        # Student
        refund = mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[0])
        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITHOUT_COUPON)

    def test_amount_assistant_with_used_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Assistant with student's used coupon
        """

        # Student
        refund = mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[0])
        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITH_COUPON)

    def test_amount_assistant_with_unused_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Assistant with student's unused coupon
        """

        # Student hasn't redeemed the coupon
        self.redeem.used = False
        self.redeem.save()

        # Student
        refund = mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[0])
        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITHOUT_COUPON)

    def test_amount_assistant_with_another_students_coupon(self):
        """
        Test the amount property with coupon associated to the order
        Assistant with other student's coupon
        """

        # Another student has a redeem with the same coupon
        another_student = mommy.make_recipe('students.student')
        mommy.make(Redeem, student=another_student, used=True, coupon=self.coupon)

        # The student hasn't redeemed his coupon
        self.redeem.used = False
        self.redeem.save()

        refund = mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[0])
        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITHOUT_COUPON)

    def test_amount_assistant_with_another_assistant_refund(self):
        """
        Test the amount property with coupon associated to the order
        Assistant with another assistant's refund
        """

        # The student has another assistant's refund from the same order
        mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[0])
        refund = mommy.make(Refund, user=self.student.user, order=self.order, assistant=self.assistants[1])

        self.assertEqual(refund.amount, self.ASSISTANT_AMOUNT_WITH_COUPON)
