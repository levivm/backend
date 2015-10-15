from django.conf import settings
from model_mommy import mommy

from activities.models import Chronogram
from orders.models import Order
from orders.serializers import OrdersSerializer
from referrals.models import Referral, CouponType, Redeem
from utils.tests import BaseAPITestCase


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
        self.calendar = mommy.make(Chronogram, activity__published=True, capacity=10)
        self.data = self.get_data()
        self.context = self.get_context()

    def get_data(self):
        return {
            'chronogram': self.calendar.id,
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
