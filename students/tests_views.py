import json
from datetime import datetime, timedelta

import mock
from django.core.urlresolvers import reverse
from mock import Mock
from model_mommy import mommy
from rest_framework import status

from activities import constants as activities_constants
from activities.factories import ActivityFactory
from activities.models import Calendar, Activity
from activities.serializers import ActivitiesSerializer, ActivitiesAutocompleteSerializer
from orders.models import Order
from students.factories import WishListFactory
from students.views import StudentViewSet
from utils.tests import BaseViewTest, BaseAPITestCase




class StudentViewTest(BaseViewTest):
    url = '/api/students/1'
    view = StudentViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_student_should_update(self):
        student = self.get_student_client()
        data = json.dumps({ 'gender': 1,'user':{'id':1,'first_name':"pablo"} })
        response = student.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"gender":1', response.content)
        self.assertIn(b'"first_name":"pablo"', response.content)

    def test_another_student_shouldnt_update(self):
        student = self.get_student_client(user_id=4)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)


class ActivitiesByStudentViewTest(BaseAPITestCase):

    def _get_context(self):
        request = Mock()
        request.user = self.student.user
        return {
            'request': request,
            'show_reviews':True
        }

    def _order_activities(self, activities):
        activities = sorted(activities, key = lambda x:x.id)
        return activities

    def _create_calendars(self, activities, date,):
        for activity in activities:
            calendar = mommy.make(Calendar, activity=activity, initial_date=date)
            mommy.make(Order, student=self.student, calendar=calendar)


    def setUp(self):
        super(ActivitiesByStudentViewTest, self).setUp()

        #get student
        student = self.student

        #create student activities
        today = datetime.today().date()
        yesterday = today - timedelta(1)
        tomorrow = today + timedelta(1)

        #create current activities
        self.current_activities = \
            ActivityFactory.create_batch(2,last_date=tomorrow)
        self._create_calendars(self.current_activities,yesterday)

        #create next activities
        self.next_activities = \
            ActivityFactory.create_batch(2)
        self._create_calendars(self.next_activities, tomorrow)

        #create past activities
        self.past_activities = \
            ActivityFactory.create_batch(2, last_date=yesterday)
        self._create_calendars(self.past_activities, yesterday)

        self.activities = Activity.objects.filter(calendars__orders__student=student)


        self.url = reverse('students:activities', kwargs={'pk':student.id})
        self.url_autocomplete = reverse('students:activities_autocomplete',
                                        kwargs={'pk':student.id})

    def test_student_activities_autocomplete(self):

        activities = self._order_activities(self.activities)
        serializer = ActivitiesAutocompleteSerializer(activities, many=True)

        # Anonymous should return forbbiden
        response = self.organizer_client.get(self.url_autocomplete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # Organizer should return forbbiden
        response = self.organizer_client.get(self.url_autocomplete)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should return data
        response = self.student_client.get(self.url_autocomplete)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


    def test_student_current_activities(self):

        data={'status': activities_constants.CURRENT}
        current_activities = self._order_activities(self.current_activities)
        serializer = ActivitiesSerializer(current_activities, many=True,
                                          context=self._get_context())

        # Anonymous should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # Organizer should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should return data
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_student_next_activities(self):

        data={'status': activities_constants.NEXT}
        next_activities = self._order_activities(self.next_activities)
        serializer = ActivitiesSerializer(next_activities, many=True,
                                          context=self._get_context())

        # Anonymous should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should return data
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_student_past_activities(self):

        data={'status': activities_constants.PAST}
        past_activities = self._order_activities(self.past_activities)
        serializer = ActivitiesSerializer(past_activities, many=True,
                                          context=self._get_context())

        # Anonymous should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should return forbbiden
        response = self.organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should return data
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)



class WishListViewTest(BaseAPITestCase):

    def setUp(self):
        super(WishListViewTest, self).setUp()

        self.url = reverse('students:wish_list')

    def test_list(self):
        """
        Test get all the activities in the wish list
        """
        wish_list = WishListFactory.create_batch(5, student=self.student)

        # Anonymous should get a 401 unauthorized
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should get a 403 forbidden
        response = self.organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should get the list
        activities = [w.activity for w in wish_list]
        response = self.student_client.get(self.url)
        request = mock.MagicMock()
        request.user = self.student.user
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'],
                         ActivitiesSerializer(activities,
                                              many=True, context={'request': request}).data)

    def test_add_activity_to_wish_list(self):
        """
        Test adding an activity to the wish list
        """

        activity = ActivityFactory()

        # Anonymous should get a 401 unauthorized
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should get a 403 forbidden
        response = self.organizer_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should be able to add an activity
        response = self.student_client.post(self.url, data={'activity_id': activity.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(activity, self.student.wish_list.all())

    def test_remove_activity_from_wish_list(self):
        """
        Test removing an activity from the wish list
        """
        activity = ActivityFactory()
        wish_list = WishListFactory(student=self.student, activity=activity)

        # Anonymous should get a 401 unauthorized
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should get a 403 forbidden
        response = self.organizer_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should be able to add an activity
        response = self.student_client.post(self.url, data={'activity_id': activity.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(activity, self.student.wish_list.all())

    def test_validate_activity_exists(self):
        # Anonymous should get a 401 unauthorized
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should get a 403 forbidden
        response = self.organizer_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student should get 400 bad request
        response = self.student_client.post(self.url, data={'activity_id': 0})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
