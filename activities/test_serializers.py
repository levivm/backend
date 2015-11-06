from datetime import datetime

from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.serializers import CalendarSerializer
from orders.models import Assistant, Order
from orders.serializers import AssistantsSerializer
from utils.serializers import UnixEpochDateField


class CalendarSerializerTest(APITestCase):
    """
    Test cases for CalendarSerializer
    """

    def setUp(self):
        self.order = mommy.make(Order, status=Order.ORDER_APPROVED_STATUS, quantity=3)
        self.assistants = mommy.make(Assistant, order=self.order, _quantity=2)
        self.calendar = self.order.calendar

    def test_read(self):
        """
        Test the serialize data
        """
        epoch = UnixEpochDateField()

        mommy.make(Assistant, order=self.order, enrolled=False)
        serializer = CalendarSerializer(self.calendar)

        content = {
            'id': self.calendar.id,
            'activity': self.calendar.activity.id,
            'initial_date': epoch.to_representation(self.calendar.initial_date),
            'closing_sale': epoch.to_representation(self.calendar.closing_sale),
            'number_of_sessions': self.calendar.number_of_sessions,
            'session_price': self.calendar.session_price,
            'capacity': self.calendar.capacity,
            'sessions': [],
            'assistants': AssistantsSerializer(self.calendar.get_assistants(), many=True).data,
            'is_weekend': self.calendar.is_weekend,
            'duration': self.calendar.duration,
            'is_free': self.calendar.is_free,
            'available_capacity': self.calendar.available_capacity(),

        }

        self.assertTrue(all(item in serializer.data.items() for item in content.items()))
