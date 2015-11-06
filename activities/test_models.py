from itertools import cycle

from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Calendar
from orders.models import Order, Assistant


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
