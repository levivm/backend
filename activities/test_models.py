import statistics
from itertools import cycle

from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Calendar, Activity
from orders.models import Order, Assistant
from reviews.models import Review


class CalendarTestCase(APITestCase):
    """
    Class to test the model Calendar
    """

    def setUp(self):
        self.calendar = mommy.make(Calendar, capacity=10)
        self.orders = self.create_orders()
        self.assistants = self.create_assistants()

    def create_orders(self):
        statuses = [Order.ORDER_APPROVED_STATUS, Order.ORDER_PENDING_STATUS,
                    Order.ORDER_DECLINED_STATUS, Order.ORDER_CANCELLED_STATUS]

        return mommy.make(Order, calendar=self.calendar, status=cycle(statuses), quantity=4, _quantity=4)

    def create_assistants(self):
        enrolled = [True, False]
        return mommy.make(Assistant, order=cycle(self.orders), enrolled=cycle(enrolled), _quantity=16)

    def test_num_enrolled(self):
        """
        Test num_enrolled property
        """

        self.assertEqual(self.calendar.num_enrolled, 4)

    def test_available_capacity(self):
        """
        Test the available capacity property
        """

        # Capacity = 10
        # Num enrolled assistants  = 4
        # Available capacity = 10 - 4 = 6

        self.assertEqual(self.calendar.available_capacity(), 6)


class ActivityTestCase(APITestCase):
    """
    Class to test the model Activity
    """

    def setUp(self):
        self.activity = mommy.make(Activity)

    def test_calculate_rating(self):
        """
        Test if recalculate the rating when a review it's created
        """

        self.assertEqual(self.activity.rating, 0)

        reviews = mommy.make(Review, activity=self.activity, rating=cycle([2, 5]), _quantity=2)
        average = statistics.mean([r.rating for r in reviews])
        self.assertEqual(self.activity.rating, average)

        reviews.pop().delete()
        average = statistics.mean([r.rating for r in reviews])
        self.assertEqual(self.activity.rating, average)
