import json

from django.core.urlresolvers import reverse
from rest_framework import status

from activities.factories import ActivityFactory
from activities.serializers import ActivitiesSerializer
from students.factories import WishListFactory
from students.views import StudentViewSet, StudentActivitiesViewSet
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


class ActivitiesByStudentViewTest(BaseViewTest):
    url = '/api/students/1/activities'
    view = StudentActivitiesViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student, response_data=b'"title":"Yoga"')
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_other_student_shouldnt_get_the_activitites(self):
        student = self.get_student_client(user_id=self.ANOTHER_STUDENT_ID)
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)


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
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], ActivitiesSerializer(activities, many=True).data)

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
