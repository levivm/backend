from itertools import cycle

import mock
from rest_framework import status
from model_mommy import mommy
from mock import Mock
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Permission

from orders.factories import OrderFactory, AssistantFactory
from orders.models import Order, Refund, Assistant
from orders.serializers import RefundSerializer
from payments.models import Fee
from utils.tests import BaseAPITestCase
from activities.models import Activity, Calendar


class OrdersAPITest(BaseAPITestCase):
    """Test orders viewset"""

    def setUp(self):
        super(OrdersAPITest, self).setUp()

        # Create Activities objects
        self.activity = mommy.make(Activity, organizer=self.organizer,
                                   published=True)
        self.other_activity = mommy.make(Activity, organizer=self.organizer,
                                         published=True)
        self.active_activity = mommy.make(Activity, published=True)
        self.inactive_activity = mommy.make(Activity)

        # Create Calendards objects
        self.calendar = mommy.make(Calendar, activity=self.activity)
        self.other_calendar = mommy.make(Calendar, activity=self.other_activity)
        self.free_calendar = mommy.make(Calendar, is_free=True,
                                        activity=self.active_activity, capacity=10)
        self.inactive_calendar = mommy.make(Calendar, activity=self.inactive_activity)
        self.full_calendar = mommy.make(Calendar, activity=self.active_activity,
                                        capacity=0)
        self.closed_enroll_calendar = mommy.make(Calendar, activity=self.active_activity,
                                                 enroll_open=False)

        # Create Orders objects
        mommy.make(Order, student=self.student, _quantity=2)
        mommy.make(Order, calendar=self.calendar, _quantity=2)
        mommy.make(Order, calendar=self.other_calendar, _quantity=2)
        self.order = mommy.make(Order, student=self.student)
        self.another_other = mommy.make(Order)

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

        self.create_inactive_activity_order_url = reverse('orders:create_or_list_by_activity',
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

        # A Student should not list student oders
        response = self.student_client.get(self.orders_by_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # List order owned by an organizer
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

    def test_create_free_order(self):
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


class RefundAPITest(BaseAPITestCase):
    """
    Class to test the api for Refund
    """

    def setUp(self):
        super(RefundAPITest, self).setUp()

        # URLs
        self.create_read_url = reverse('orders:refund_api')
        self.read_organizer_url = reverse('orders:refund_api', kwargs={'organizer_id': self.organizer.id})


        #Serializers context
        request = Mock()
        request.user = self.organizer.user
        self.organizer_context = { 'request': request}
        request = Mock()
        request.user = self.student.user
        self.student_context = { 'request': request}

        # Arrangement
        calendars = [
            mommy.make(Calendar, activity__organizer=self.organizer),
            mommy.make(Calendar, activity__organizer=self.another_organizer)
        ]
        self.orders = mommy.make(Order, _quantity=3, amount=cycle([100, 200, 300]), calendar=cycle(calendars))
        self.student_refunds = mommy.make(Refund, user=self.student.user,
                                          _quantity=50, order=cycle(self.orders))
        self.organizer_refunds = mommy.make(Refund, user=self.organizer.user, _quantity=30,
                                            order=cycle(self.orders))

        # Permissions
        permission = Permission.objects.get_by_natural_key('add_refund', 'orders', 'refund')
        permission.user_set.add(self.student.user)
        permission.user_set.add(self.organizer.user)

    def test_read(self):
        """
        Test case for list an user's refund
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.create_read_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return data
        serializer = RefundSerializer(self.student_refunds[:10], many=True,
                                      context=self.student_context)
        response = self.student_client.get(self.create_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Organizer should return data
        serializer = RefundSerializer(self.organizer_refunds[:10], many=True,
                                        context=self.organizer_context)
        response = self.organizer_client.get(self.create_read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data, response)

    @mock.patch('orders.tasks.SendEMailStudentRefundTask.delay')
    def test_create_student(self, delay):
        """
        Test create a refund for a Student
        """

        order = mommy.make(Order, student=self.student, status=Order.ORDER_APPROVED_STATUS)
        assistant = mommy.make(Assistant, order=order)
        data = {
            'order': order.id,
            'assistant': assistant.id,
            'status': 'approved',
        }

        # Anonymous should return unauthorized
        response = self.client.post(self.create_read_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should create a refund
        response = self.student_client.post(self.create_read_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Refund.objects.filter(user=self.student.user, order=order, status='pending',
                                              assistant=assistant).exists())

    @mock.patch('orders.tasks.SendEMailStudentRefundTask.delay')
    def test_create_organizer(self, delay):
        """
        Test create a refund for an Organizer
        """

        order = mommy.make(Order, calendar__activity__organizer=self.organizer, status=Order.ORDER_APPROVED_STATUS)
        assistant = mommy.make(Assistant, order=order)
        data = {
            'order': order.id,
            'assistant': assistant.id,
            'status': 'approved',
        }

        # Organizer should create a refund
        response = self.organizer_client.post(self.create_read_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.content)
        self.assertTrue(Refund.objects.filter(user=self.organizer.user, order=order, status='pending').exists())

    @mock.patch('orders.tasks.SendEMailStudentRefundTask.delay')
    def test_order_refund(self, delay):
        """
        Test full order refund
        """

        order = OrderFactory(student=self.student, status=Order.ORDER_APPROVED_STATUS)
        AssistantFactory.create_batch(4, order=order, enrolled=True)

        data = {
            'order': order.id,
        }

        response = self.student_client.post(self.create_read_url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Refund.objects.filter(user=self.student.user, order=order, status='pending').exists())

    def test_pagination(self):
        """
        Test case for pagination when list the refunds
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.create_read_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return paginated data
        serializer = RefundSerializer(self.student_refunds[10:20], many=True,
                                    context=self.student_context)
        response = self.student_client.get(self.create_read_url, data={'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Organizer should return paginated data
        serializer = RefundSerializer(self.organizer_refunds[10:20], many=True,
                                      context=self.organizer_context)
        response = self.organizer_client.get(self.create_read_url, data={'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_read_refunds_organizer_activities(self):
        """
        Test list refunds of an organizer's activities
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.read_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.get(self.read_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should return data
        queryset = Refund.objects.filter(order__calendar__activity__organizer=self.organizer)[:10]
        serializer = RefundSerializer(queryset, many=True,context=self.organizer_context)
        response = self.organizer_client.get(self.read_organizer_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
