import json
from guardian.shortcuts import assign_perm

from rest_framework import status
from django.http.request import HttpRequest
from django.contrib.auth.models import User
from activities.models import Activity

from organizers.models import Instructor, Organizer
from organizers.views import OrganizerViewSet, OrganizerInstructorViewSet, OrganizerLocationViewSet, InstructorViewSet, \
    ActivityInstructorViewSet
from locations.serializers import LocationsSerializer
from trulii.constants import MAX_ACTIVITY_INSTRUCTORS
from utils.tests import BaseViewTest


class OrganizerViewTest(BaseViewTest):
    url = '/api/organizers/1'
    view = OrganizerViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_edit_own_organizer(self):
        client = self.get_organizer_client()
        data = json.dumps({"name": "Another Name"})
        response = client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"name":"Another Name"', response.content)

    def test_organizer_shouldnt_edit_another_organizer(self):
        client = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        data = json.dumps({"name": "Second Organizer"})
        response = client.put(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizerActivitiesViewTest(BaseViewTest):
    url = '/api/organizers/1/activities'
    view = OrganizerViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


class OrganizerLocationsViewTest(BaseViewTest):
    url = '/api/organizers/1/locations'
    view = OrganizerLocationViewSet
    ORGANIZER_ID = 1

    def _get_location_data(self):
        return {
            "id": 2,
            "city": 1,
            "point": [4.610676392396654, -74.07760244445802],
            "address": "Address Here"
        }

    def __init__(self, methodName='runTest'):
        super(OrganizerLocationsViewTest, self).__init__(methodName)
        self.url = '/api/organizers/%s/locations' % self.ORGANIZER_ID

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_own_location(self):
        client = self.get_organizer_client()
        data = json.dumps(self._get_location_data())
        response = client.post(self.url, data, **self.headers)
        expected_organizer_id = bytes('"organizer":%s' % self.ORGANIZER_ID, 'utf8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(expected_organizer_id, response.content)
        self.assertIn(b'"point":[4.610676392396654,-74.07760244445802]', response.content)

    def test_other_organizer_shouldnt_create_location(self):
        client = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        data = json.dumps(self._get_location_data())
        response = client.post(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_permissions_of_location(self):
        request = HttpRequest()
        request.user = User.objects.get(id=self.ORGANIZER_ID)
        request.data = request.data = self._get_location_data()
        serializer = LocationsSerializer(data=request.data, \
                                         context={'request': request, 'organizer_location': True})
        serializer.is_valid(raise_exception=True)
        location = serializer.save()
        self.assertTrue(request.user.has_perm('locations.add_location'))
        self.assertTrue(request.user.has_perm('locations.change_location', location))
        self.assertTrue(request.user.has_perm('locations.delete_location', location))


class OrganizersInstructorsViewTest(BaseViewTest):
    url = '/api/organizers/1/instructors/'
    view = OrganizerInstructorViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_the_instructors(self):
        organizer = Organizer.objects.get(user__id=self.ORGANIZER_ID)
        instructors_count = Instructor.objects.count()
        organizer_instructors = organizer.instructors.count()
        client = self.get_organizer_client()
        data = {
            'full_name': 'Instructor 2',
            'organizer': 2,
            'website': 'www.instructor2.com',
        }
        response = client.post(self.url, data=json.dumps(data), **self.headers)
        instructor = Instructor.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Instructor.objects.count(), instructors_count + 1)
        self.assertEqual(instructor.organizer, organizer)
        self.assertEqual(organizer.instructors.count(), organizer_instructors + 1)
        self.assertTrue(organizer.user.has_perm(perm='organizers.change_instructor', obj=instructor))
        self.assertTrue(organizer.user.has_perm(perm='organizers.delete_instructor', obj=instructor))

    def test_another_organizer_methods(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)


class InstructorViewTest(BaseViewTest):
    INSTRUCTOR_ID = 1
    view = InstructorViewSet

    def __init__(self, methodName='runTest'):
        super(InstructorViewTest, self).__init__(methodName)
        self.url = '/api/instructors/%s' % self.INSTRUCTOR_ID

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_update_an_instructor(self):
        name = 'Destructor'
        organizer = self.get_organizer_client()
        data = {
            'full_name': name,
            'organizer': 2,
        }
        response = organizer.put(self.url, data=json.dumps(data), **self.headers)
        instructor = Instructor.objects.get(id=self.INSTRUCTOR_ID)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(instructor.full_name, name)
        self.assertEqual(instructor.organizer.id, 1)

    def test_organizer_should_delete_an_instructor(self):
        organizer = Organizer.objects.get(user__id=self.ORGANIZER_ID)
        instructors_count = Instructor.objects.count()
        organizer_instructors = organizer.instructors.count()
        client = self.get_organizer_client()
        response = client.delete(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Instructor.objects.count(), instructors_count - 1)
        self.assertEqual(organizer.instructors.count(), organizer_instructors - 1)

    def test_another_organizer_shouldnt_update_or_delete_an_instructor(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


class ActivityInstructorsGetAndPostViewTest(BaseViewTest):
    ACTIVITY_ID = 1
    view = ActivityInstructorViewSet

    def __init__(self, methodName='runTest'):
        super(ActivityInstructorsGetAndPostViewTest, self).__init__(methodName)
        self.url = '/api/activities/%s/instructors' % self.ACTIVITY_ID

    def get_data(self):
        return {
            'full_name': 'Instructor 2',
            'organizer': 2,
            'website': 'www.instructor2.com',
        }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_get_the_instructors(self):
        organizer = self.get_organizer_client()
        response = organizer.get(self.url, **self.headers)
        instructor = Instructor.objects.get(id=1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(bytes(instructor.full_name, 'utf8'), response.content)
        self.assertEqual(len(response.data), 1)

    def test_organizer_should_create_and_associate_the_instructor(self):
        organizer = Organizer.objects.get(user__id=self.ORGANIZER_ID)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        instructors_count = Instructor.objects.count()
        organizer_instructors = organizer.instructors.count()
        activity_instructors = activity.instructors.count()
        client = self.get_organizer_client()
        data = self.get_data()
        response = client.post(self.url, data=json.dumps(data), **self.headers)
        instructor = Instructor.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Instructor.objects.count(), instructors_count + 1)
        self.assertEqual(organizer.instructors.count(), organizer_instructors + 1)
        self.assertEqual(activity.instructors.count(), activity_instructors + 1)
        self.assertEqual(instructor.organizer, organizer)
        self.assertTrue(activity.instructors.filter(id=instructor.id).exists())
        self.assertTrue(organizer.user.has_perm(perm='organizers.change_instructor', obj=instructor))
        self.assertTrue(organizer.user.has_perm(perm='organizers.delete_instructor', obj=instructor))

    def test_another_organizer_shouldnt_get_or_create_an_instructor(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_shouldnt_create_an_instructor_if_activity_has_max(self):
        organizer = self.get_organizer_client()
        data = self.get_data()
        for i in range(1, MAX_ACTIVITY_INSTRUCTORS):
            organizer.post(self.url, data=json.dumps(data), **self.headers)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        response = organizer.post(self.url, data=json.dumps(data), **self.headers)
        self.assertEqual(activity.instructors.count(), MAX_ACTIVITY_INSTRUCTORS)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ActivityInstructorsUpdateAndDeleteViewTest(BaseViewTest):
    ACTIVITY_ID = 1
    INSTRUCTOR_ID = 1
    view = ActivityInstructorViewSet

    def __init__(self, methodName='runTest'):
        super(ActivityInstructorsUpdateAndDeleteViewTest, self).__init__(methodName)
        self.url = '/api/activities/%s/instructors/%s' % (self.ACTIVITY_ID, self.INSTRUCTOR_ID)

    def get_data(self, name):
        return {
            'full_name': name,
            'organizer': 2,
        }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_associate_an_instructor(self):
        name = 'Destructor'
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        instructor = Instructor.objects.get(id=self.INSTRUCTOR_ID)
        activity.instructors.clear()
        activity_instructors = activity.instructors.count()
        organizer = self.get_organizer_client()
        data = self.get_data(name=name)
        response = organizer.put(self.url, data=json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], name)
        self.assertEqual(response.data['organizer'], 1)
        self.assertEqual(activity.instructors.count(), activity_instructors + 1)
        self.assertTrue(activity.instructors.filter(id=instructor.id).exists())

    def test_organizer_should_disassociate_an_instructor(self):
        organizer = self.get_organizer_client()
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        instructor = Instructor.objects.get(id=self.INSTRUCTOR_ID)
        activity_instructors = activity.instructors.count()
        response = organizer.delete(self.url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Instructor.objects.filter(id=instructor.id).exists())
        self.assertEqual(activity.instructors.count(), activity_instructors - 1)
        self.assertFalse(activity.instructors.filter(id=instructor.id).exists())

    def test_another_organizer_shouldnt_associate_or_disassociate_an_instructor(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_shouldnt_associate_an_instructor_if_activity_has_max(self):
        client = self.get_organizer_client()
        organizer = Organizer.objects.get(user__id=self.ORGANIZER_ID)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        data_post = {
            'full_name': 'Instructor 2',
            'organizer': organizer,
            'website': 'www.instructor2.com',
        }
        instructor = Instructor.objects.create(**data_post)
        assign_perm(perm='organizers.change_instructor', user_or_group=organizer.user, obj=instructor)
        data_post.update({'organizer': 2})
        for i in range(1, MAX_ACTIVITY_INSTRUCTORS):
            client.post('/api/activities/%s/instructors' % self.ACTIVITY_ID, data=json.dumps(data_post), **self.headers)
        data = self.get_data(name='Destructor')
        url = '/api/activities/%s/instructors/%s' % (self.ACTIVITY_ID, instructor.id)
        response = client.put(url, data=json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(activity.instructors.count(), MAX_ACTIVITY_INSTRUCTORS)
        self.assertFalse(activity.instructors.filter(id=instructor.id).exists())
