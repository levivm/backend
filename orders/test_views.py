from datetime import timedelta

import mock

from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status

from activities.factories import ActivityFactory, CalendarFactory
from activities.models import Activity, Calendar
from orders.factories import OrderFactory
from orders.models import Order
from referrals.factories import CouponFactory
from utils.tests import BaseAPITestCase


class OrdersAPITest(BaseAPITestCase):
    """Test orders viewset"""

    def setUp(self):
        super(OrdersAPITest, self).setUp()

        # Create Activities objects
        self.activity = ActivityFactory(organizer=self.organizer,
                                   published=True)
        self.other_activity = ActivityFactory(organizer=self.organizer,
                                         published=True)
        self.active_activity = ActivityFactory(published=True)
        self.inactive_activity = ActivityFactory()

        # Create Calendards objects
        self.calendar = mommy.make(Calendar, activity=self.activity)
        self.other_calendar = mommy.make(Calendar, activity=self.other_activity)
        self.free_calendar = mommy.make(Calendar, is_free=True,
                                        activity=self.active_activity, available_capacity=10)
        self.inactive_calendar = mommy.make(Calendar, activity=self.inactive_activity)
        self.full_calendar = mommy.make(Calendar, activity=self.active_activity,
                                        available_capacity=0)
        self.closed_enroll_calendar = mommy.make(Calendar, activity=self.active_activity,
                                                 enroll_open=False)

        # Create Orders objects
        OrderFactory.create_batch(student=self.student, size=2)
        OrderFactory.create_batch(calendar=self.calendar, size=2)
        OrderFactory.create_batch(calendar=self.other_calendar, size=2)
        self.order = OrderFactory(student=self.student)
        self.another_other = OrderFactory()

        # URLs
        self.orders_by_activity_url = reverse('orders:create_or_list_by_activity',
                                              kwargs={'activity_pk': self.activity.id})

        self.orders_by_student_url = reverse('orders:list_by_student',
                                             kwargs={'student_pk': self.student.id})

        self.orders_by_organizer_url = reverse('orders:list_by_organizer',
                                               kwargs={'organizer_pk': self.organizer.id})

        self.order_retrieve_url = reverse('orders:retrieve',
                                          kwargs={'order_pk': self.order.id})

        self.another_order_retrieve_url = reverse('orders:retrieve',
                                                  kwargs={'order_pk': self.another_other.id})

        self.create_order_url = reverse('orders:create_or_list_by_activity',
                                        kwargs={'activity_pk': self.active_activity.id})

        self.create_inactive_activity_order_url = reverse(
            'orders:create_or_list_by_activity',
            kwargs={'activity_pk': self.inactive_activity.id})

        # Set permissions
        permission = Permission.objects.get_by_natural_key('add_order',
                                                           'orders', 'order')
        permission.user_set.add(self.student.user)

        # counts
        self.orders_count = Order.objects.all().count()
        self.student_orders_count = Order.objects.filter(student=self.student).count()
        self.activity_orders_count = Order.objects.filter(calendar=self.calendar).count()
        self.organizer_orders_count = Order.objects. \
            filter(calendar__activity__organizer=self.organizer).count()

    def get_order_data(self, activity_id, calendar_id):
        return {
            'calendar': calendar_id,
            'activity': activity_id,
            'quantity': 1,
            'amount': 8000,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }

    def test_list_by_activity(self):
        """
        Test to list orders by activities owned by an organizer
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.orders_by_activity_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # A student should not list an activity oders
        response = self.student_client.get(self.orders_by_activity_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # List activity orders
        response = self.organizer_client.get(self.orders_by_activity_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), self.activity_orders_count)

    def test_list_by_student(self):
        """
        Test to list orders by student
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.orders_by_student_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # An organizer should not list student oders
        response = self.organizer_client.get(self.orders_by_student_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # List order owned by a student
        response = self.student_client.get(self.orders_by_student_url)
        orders_owner = response.data['results'][0].get('student').get('id')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.student_orders_count)
        self.assertEqual(orders_owner, self.student.id)

    def test_list_by_organizer(self):
        """
        Test to list orders by organizer
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.orders_by_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # A Student should not list student orders
        response = self.student_client.get(self.orders_by_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # List order owned by an organizer
        Order.objects.filter(calendar__activity__organizer=self.organizer).\
            update(status=Order.ORDER_APPROVED_STATUS)
        response = self.organizer_client.get(self.orders_by_organizer_url)
        order_id = response.data['results'][0].get('id')
        orders_owner = Order.objects.get(id=order_id).calendar. \
            activity.organizer.id
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.organizer_orders_count)
        self.assertEqual(orders_owner, self.organizer.id)

    def test_retrieve(self):
        """
        Test to retrieve an order by pk
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.order_retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # An organizer should not retrieve student oders
        # response = self.organizer_client.get(self.order_retrieve_url)
        # self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # A student should not retrieve other student order
        response = self.student_client.get(self.another_order_retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # A student should retrieve his order
        response = self.student_client.get(self.order_retrieve_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_closed_enroll_calender_order(self):
        """Test to create an order over an calendar with closed enrollment"""

        post_data = self.get_order_data(self.active_activity.id, self.closed_enroll_calendar.id)

        # A student should not create an order if the activity is inactive
        response = self.student_client.post(self.create_order_url,
                                            post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), self.orders_count)

    def test_create_full_calender_order(self):
        """Test to create an order over an full calendar"""

        post_data = self.get_order_data(self.active_activity.id, self.full_calendar.id)

        # A student should not create an order if the activity is inactive
        response = self.student_client.post(self.create_order_url,
                                            post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), self.orders_count)

    def test_create_inactive_activity_order(self):
        """Test to create an order over an inactive activity"""

        post_data = self.get_order_data(self.inactive_activity.id, self.inactive_calendar.id)

        # Anonymous should return unauthorized
        response = self.client.post(self.create_inactive_activity_order_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # An organizer should not create a free order
        response = self.organizer_client.post(self.create_inactive_activity_order_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # A student should not create an order if the activity is inactive
        response = self.student_client.post(self.create_inactive_activity_order_url,
                                            post_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), self.orders_count)

    @mock.patch('referrals.tasks.SendCouponEmailTask.s')
    @mock.patch('payments.tasks.SendPaymentEmailTask.s')
    @mock.patch('payments.tasks.SendNewEnrollmentEmailTask.s')
    def test_create_free_order(self, new_enrollment, payment_email, coupon_email):
        """
        Test to create a order over a free calendar
        """

        # Post data
        post_data = self.get_order_data(self.active_activity.id, self.free_calendar.id)

        # Anonymous should return unauthorized
        response = self.client.post(self.create_order_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # An organizer should not create a free order
        response = self.organizer_client.post(self.create_order_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # A student should create a free order
        response = self.student_client.post(self.create_order_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), self.orders_count + 1)
