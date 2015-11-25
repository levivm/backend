from datetime import datetime

from django.utils.timezone import now
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.models import Calendar, CalendarSession
from activities.serializers import CalendarSerializer
from orders.models import Assistant, Order
from orders.serializers import AssistantsSerializer
from utils.serializers import UnixEpochDateField


class CalendarSerializerTest(APITestCase):
    """
    Test cases for CalendarSerializer
    """

    def setUp(self):
        self.calendar = mommy.make(Calendar, session_price=100000)
        self.order = mommy.make(Order, status=Order.ORDER_APPROVED_STATUS, calendar=self.calendar, quantity=3)
        self.assistants = mommy.make(Assistant, order=self.order, _quantity=2)

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

    def test_validate_change_price(self):
        """
        It shouldn't change the price if there is assistants enrolled
        """

        now_unix_timestamp = int(now().timestamp()) * 1000

        data = {
            'session_price': 54321,
            'sessions':[{
                'date': now_unix_timestamp,
                'start_time': now_unix_timestamp,
                'end_time': now_unix_timestamp + 100000,
            }],
            'closing_sale': now_unix_timestamp,
        }
        current_session_price = self.calendar.session_price

        with self.assertRaisesMessage(ValidationError, "{'session_price': ['No se puede cambiar el precio "
                                                       "cuando hay estudiantes inscritos']}"):
            serializer = CalendarSerializer(self.calendar, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        self.assertEqual(Calendar.objects.get(id=self.calendar.id).session_price, current_session_price)
