import json
from datetime import datetime, timedelta
from model_mommy import mommy
from rest_framework import status
from django.core.urlresolvers import reverse
from orders.models import Order
from activities.models import Calendar
from activities.factories import ActivityFactory
from activities.serializers import ActivitiesSerializer
from activities import constants as activities_constants
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


class ActivitiesByStudentViewTest(BaseAPITestCase):

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

        self.url = reverse('students:activities', kwargs={'pk':student.id})

    def test_student_current_activities(self):

        data={'status': activities_constants.CURRENT}
        current_activities = self._order_activities(self.current_activities)
        serializer = ActivitiesSerializer(current_activities, many=True)

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
        serializer = ActivitiesSerializer(next_activities, many=True)

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
        serializer = ActivitiesSerializer(past_activities, many=True)

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


# class SendEmailStudentSignupTaskTest(BaseViewTest):
#     STUDENT_ID = 1
#     # url = '/api/students/1/activities'

#     def test_task_dispatch_if_there_is_not_other_task(self):
#         # student = self.get_student_client()
#         # from rest_framework.test import APIRequestFactory
#         # factory = APIRequestFactory()
#         # data = {
#         #     'first_name':'first_name',
#         #     'last_name':'last_name',
#         #     'login':'lolpe@gmail.com',
#         #     'password':'19737450',
#         #     'user_type':'S'
#         # }
#         # student = self.get_student_client()
#         # request = factory.post('/api/users/signup', data, format='json')
#         # import pdb
#         # pdb.set_trace()
#         task = SendEmailStudentSignupTask()
#         # task.request = request
#         result = task.apply((self.STUDENT_ID, ),)
#         self.assertEqual(result.result, 'Task scheduled')

#     def test_ignore_task_if_there_is_a_pending_task(self):
#         task = SendEmailStudentSignupTask()
#         task.apply((self.STUDENT_ID, False), countdown=60)
#         task2 = SendEmailStudentSignupTask()
#         result = task2.apply((self.STUDENT_ID, False))
#         self.assertEqual(result.result, None)


#     def test_task_should_delete_on_success(self):
#         task = SendEmailStudentSignupTask()
#         task.apply((self.STUDENT_ID, ))
#         self.assertEqual(CeleryTask.objects.count(), 0)


