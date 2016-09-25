import statistics
from itertools import cycle

from django.utils.timezone import now
from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.factories import ActivityFactory, ActivityPhotoFactory, \
    CalendarFactory
from activities.models import Calendar
from orders.models import Order, Assistant
from reviews.models import Review
from users.factories import UserFactory


class CalendarTestCase(APITestCase):
    """
    Class to test the model Calendar
    """

    def setUp(self):
        self.calendar = CalendarFactory(available_capacity=10)
        self.orders = self.create_orders()
        self.assistants = self.create_assistants()

    def create_orders(self):
        statuses = [Order.ORDER_APPROVED_STATUS, Order.ORDER_PENDING_STATUS,
                    Order.ORDER_DECLINED_STATUS, Order.ORDER_CANCELLED_STATUS]
        orders = mommy.make(Order, calendar=self.calendar, status=cycle(statuses), quantity=4, _quantity=4)
        return orders

    def create_assistants(self):
        enrolled = [True, False]
        return mommy.make(Assistant, order=cycle(self.orders), enrolled=cycle(enrolled), _quantity=16)

    def test_available_capacity(self):
        """
        Test the available capacity property
        """

        # Capacity = 10
        # Num enrolled assistants  = 4
        # Available capacity = 10 - 4 = 6

        self.assertEqual(self.calendar.available_capacity, 6)

        # Capacity = 10
        # Num enrolled assistants  = 4
        # Available capacity = 10 - 4 = 6
        # Cancel assistant
        # Num enrolled assistants  = 4 - 1 = 3
        # Available capacity = 10 - 3  = 7

        approved_order = self.orders[0]
        assistants = approved_order.assistants.all()
        first_assistant = assistants[0]
        first_assistant.enrolled = False
        first_assistant.save()

        self.assertEqual(self.calendar.available_capacity, 7)

        # Capacity = 10
        # Num enrolled assistants  = 4
        # Available capacity = 10 - 4 = 6
        # Cancel assistant
        # Num enrolled assistants  = 4 - 1 = 3
        # Available capacity = 10 - 3  = 7
        # Cancel order
        # Num enrolled assistants  = 3 - 3 = 0
        # Available capacity = 10 - 0  = 10

        approved_order.change_status(Order.ORDER_CANCELLED_STATUS)

        self.assertEqual(self.calendar.available_capacity, 10)

        # Capacity = 10
        # Num enrolled assistants  = 4
        # Available capacity = 10 - 4 = 6
        # Cancel assistant
        # Num enrolled assistants  = 4 - 1 = 3
        # Available capacity = 10 - 3  = 7
        # Cancel order
        # Num enrolled assistants  = 3 - 3 = 0
        # Available capacity = 10 - 0  = 10
        # Approve order
        # Num enrolled assistants  = 0 + 3 = 0
        # Available capacity = 10 - 3  = 7
        approved_order.change_status(Order.ORDER_APPROVED_STATUS)

        self.assertEqual(self.calendar.available_capacity, 7)


    def test_permissions(self):
        """
        When an instance is created should set the permissions
        """

        user = self.calendar.activity.organizer.user

        self.assertTrue(user.has_perm('activities.change_calendar', self.calendar))
        self.assertTrue(user.has_perm('activities.delete_calendar', self.calendar))

    def test_get_assistants(self):
        """
        Test the method get_assistants
        """

        assistants = Assistant.objects.filter(
                order__calendar=self.calendar,
                order__status__in=[Order.ORDER_APPROVED_STATUS, Order.ORDER_PENDING_STATUS],
                enrolled=True)
        self.assertEqual(self.calendar.get_assistants(), list(assistants))

class ActivityTestCase(APITestCase):
    """
    Class to test the model Activity
    """

    def setUp(self):
        self.activity = ActivityFactory()

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

    def test_permissions(self):
        """
        When an instance is created should set the permissions
        """

        user = self.activity.organizer.user
        self.assertTrue(user.has_perm('activities.change_activity', self.activity))


class ActivityPhotoTestCase(APITestCase):
    """
    Class to test the model ActivityPhoto
    """

    def setUp(self):
        self.user = UserFactory()
        self.activity = ActivityFactory(organizer__user=self.user)

    def test_permissions(self):
        """
        When an instance is created should set the permissions
        """

        activity_photo = ActivityPhotoFactory(activity=self.activity)
        self.assertTrue(self.user.has_perm('activities.delete_activityphoto', activity_photo))
