import json
from datetime import datetime, timedelta

import mock
from django.contrib.auth.models import User, Permission
from django.core.urlresolvers import reverse
from django.http.request import HttpRequest
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from rest_framework import status

from activities import constants as activities_constants
from activities.factories import ActivityFactory
from activities.models import Activity
from activities.serializers import ActivitiesSerializer, ActivitiesAutocompleteSerializer
from locations.serializers import LocationsSerializer
from organizers.models import Instructor, Organizer, OrganizerBankInfo
from organizers.views import OrganizerViewSet, OrganizerInstructorViewSet, \
    OrganizerLocationViewSet, InstructorViewSet, \
    ActivityInstructorViewSet
from utils.tests import BaseViewTest, BaseAPITestCase


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


class OrganizerActivitiesViewTest(BaseAPITestCase):
    def _order_activities(self, activities):
        activities = sorted(activities, key=lambda x: x.id, reverse=True)
        return activities

    def setUp(self):
        super(OrganizerActivitiesViewTest, self).setUp()

        # get organizer
        organizer = self.organizer

        # create organizer activities
        today = datetime.today().date()
        yesterday = today - timedelta(1)

        self.unpublished_activities = \
            ActivityFactory.create_batch(2, organizer=organizer)

        self.opened_activities = \
            ActivityFactory.create_batch(2, published=True,
                                         organizer=organizer, last_date=today)

        self.closed_activities = \
            ActivityFactory.create_batch(2, published=True,
                                         organizer=organizer, last_date=yesterday)

        self.activities = self.organizer.activity_set.all()

        # set url
        self.url = reverse('organizers:activities', kwargs={'organizer_pk': organizer.id})
        self.autocomplete_url = reverse('organizers:activities_autocomplete',
                                        kwargs={'organizer_pk': organizer.id})

    def test_organizer_unpublished_activities(self):
        data = {'status': activities_constants.UNPUBLISHED}
        opened_activities = self._order_activities(self.unpublished_activities)
        serializer = ActivitiesSerializer(opened_activities, many=True)

        # Anonymous should return unauthorized
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Another organizer should return forbidden
        response = self.another_organizer_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should return data
        response = self.organizer_client.get(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_organizer_closed_activities(self):
        data = {'status': activities_constants.CLOSED}
        closed_activities = self._order_activities(self.closed_activities)
        request = mock.MagicMock()

        # Anonymous should return data
        response = self.client.get(self.url, data=data)
        serializer = ActivitiesSerializer(closed_activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Student should return data
        request.user = self.student.user
        serializer = ActivitiesSerializer(closed_activities, many=True,
                                          context={'request': request})
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Organizer should return data
        request.user = self.organizer.user
        serializer = ActivitiesSerializer(closed_activities, many=True,
                                          context={'request': request})
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_organizer_opened_activities(self):
        data = {'status': activities_constants.OPENED}
        opened_activities = self._order_activities(self.opened_activities)
        request = mock.MagicMock()

        # Anonymous should return data
        response = self.client.get(self.url, data=data)
        serializer = ActivitiesSerializer(opened_activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Student should return data
        request.user = self.student.user
        serializer = ActivitiesSerializer(opened_activities, many=True,
                                          context={'request': request})
        response = self.student_client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

        # Organizer should return data
        request.user = self.organizer.user
        serializer = ActivitiesSerializer(opened_activities, many=True,
                                          context={'request': request})
        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_organizer_activities_autocomplete(self):
        serializer = ActivitiesAutocompleteSerializer(self.activities, many=True)
        response = self.organizer_client.get(self.autocomplete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


class OrganizerLocationsViewTest(BaseViewTest):
    url = '/api/organizers/1/locations'
    view = OrganizerLocationViewSet
    ORGANIZER_ID = 1

    def _get_location_data(self):
        return {
            "id": 2,
            "city": 1,
            "point": [4, -74],
            "address": "Address Here",
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
        self.method_should_be(clients=organizer, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_own_location(self):
        client = self.get_organizer_client()
        data = json.dumps(self._get_location_data())
        response = client.post(self.url, data, **self.headers)
        rjson = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue("'organizer': %d" % self.ORGANIZER_ID in str(rjson))
        self.assertTrue("'point': [4.0, -74.0]" in str(rjson))

    def test_other_organizer_shouldnt_create_location(self):
        client = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        data = json.dumps(self._get_location_data())
        response = client.post(self.url, data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_permissions_of_location(self):
        request = HttpRequest()
        request.user = User.objects.get(id=self.ORGANIZER_ID)
        request.data = request.data = self._get_location_data()
        serializer = LocationsSerializer(data={**request.data, 'organizer': self.ORGANIZER_ID},
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
        self.method_should_be(clients=organizer, method='put',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        self.assertTrue(
            organizer.user.has_perm(perm='organizers.change_instructor', obj=instructor))
        self.assertTrue(
            organizer.user.has_perm(perm='organizers.delete_instructor', obj=instructor))

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
        self.method_should_be(clients=organizer, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        self.assertTrue(
            organizer.user.has_perm(perm='organizers.change_instructor', obj=instructor))
        self.assertTrue(
            organizer.user.has_perm(perm='organizers.delete_instructor', obj=instructor))

    def test_another_organizer_shouldnt_get_or_create_an_instructor(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_shouldnt_create_an_instructor_if_activity_has_max(self):
        organizer = self.get_organizer_client()
        data = self.get_data()
        for i in range(1, activities_constants.MAX_ACTIVITY_INSTRUCTORS):
            organizer.post(self.url, data=json.dumps(data), **self.headers)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        response = organizer.post(self.url, data=json.dumps(data), **self.headers)
        self.assertEqual(activity.instructors.count(), activities_constants.MAX_ACTIVITY_INSTRUCTORS)
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
        assign_perm(perm='organizers.change_instructor', user_or_group=organizer.user,
                    obj=instructor)
        data_post.update({'organizer': 2})
        for i in range(1, activities_constants.MAX_ACTIVITY_INSTRUCTORS):
            client.post('/api/activities/%s/instructors' % self.ACTIVITY_ID,
                        data=json.dumps(data_post), **self.headers)
        data = self.get_data(name='Destructor')
        url = '/api/activities/%s/instructors/%s' % (self.ACTIVITY_ID, instructor.id)
        response = client.put(url, data=json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(activity.instructors.count(), activities_constants.MAX_ACTIVITY_INSTRUCTORS)
        self.assertFalse(activity.instructors.filter(id=instructor.id).exists())


class OrganizerBankInfoAPITest(BaseAPITestCase):
    """
    Class to test the api cases of Organizer Bank Info
    """

    def setUp(self):
        super(OrganizerBankInfoAPITest, self).setUp()

        # URLs
        self.bank_info_api_url = reverse('organizers:bank_info_api')
        self.bank_choices = reverse('organizers:bank_choices')

        # POST data
        self.data = {
            'organizer': self.organizer.id,
            'beneficiary': 'Beneficiario',
            'bank': 'bancolombia',
            'document_type': 'cc',
            'document': '123456789',
            'account_type': 'ahorros',
            'account': '987654321-0',
        }

        # Permissions
        add_organizerbankinfo = Permission.objects.get_by_natural_key('add_organizerbankinfo',
                                                                      'organizers',
                                                                      'organizerbankinfo')
        change_organizerbankinfo = Permission.objects.get_by_natural_key(
            'change_organizerbankinfo', 'organizers', 'organizerbankinfo')
        add_organizerbankinfo.user_set.add(self.organizer.user, self.another_organizer.user)
        change_organizerbankinfo.user_set.add(self.organizer.user, self.another_organizer.user)

    def test_create(self):
        """
        Test create view
        """

        # Anonymous should return unauthorized
        response = self.client.post(self.bank_info_api_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.post(self.bank_info_api_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should create the bank info
        response = self.organizer_client.post(self.bank_info_api_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.data.update({
            'bank': 'BANCOLOMBIA'
        })
        self.assertTrue(all(item in response.data.items() for item in self.data.items()))
        self.assertTrue(
            OrganizerBankInfo.objects.filter(organizer=self.organizer,
                                             beneficiary=self.data['beneficiary']).exists())

    def test_read(self):
        """
        Test read method of view
        """

        # Arrangement
        mommy.make(OrganizerBankInfo, **{**self.data, 'organizer': self.organizer})

        # Anonymous should return unauthorized
        response = self.client.get(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.get(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should get data
        self.data.update({
            'bank': 'BANCOLOMBIA'
        })
        response = self.organizer_client.get(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item in response.data.items() for item in self.data.items()))

        # Organizer without bankinfo should return an empty dict
        response = self.another_organizer_client.get(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {})

    def test_update(self):
        """
        Test update method
        """

        # Arrangement
        data = self.data.copy()
        data['organizer'] = self.organizer
        bank_info = mommy.make(OrganizerBankInfo, **data)
        post_data = {'beneficiary': 'Harvey', 'account_type': 'corriente'}
        updated_data = self.data.copy()
        updated_data['organizer_id'] = updated_data.pop('organizer')
        updated_data.update(post_data)

        # Anonymous should return unauthorized
        response = self.client.put(self.bank_info_api_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.put(self.bank_info_api_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer shouldn't update
        response = self.organizer_client.put(self.bank_info_api_url, post_data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # response = self.organizer_client.put(self.bank_info_api_url, post_data)
        # bank_info = OrganizerBankInfo.objects.get(id=bank_info.id)
        # self.assertEqual(response.status_code, status.HTTP_200_OK)
        # self.assertTrue(bank_info.beneficiary == post_data['beneficiary'])
        # self.assertTrue(bank_info.account_type == post_data['account_type'])
        # self.assertTrue(all(item in bank_info.__dict__.items() for item in updated_data.items()))

    def test_delete(self):
        """
        Test delete
        """

        # Arrangement
        data = self.data.copy()
        data['organizer'] = self.organizer
        mommy.make(OrganizerBankInfo, **data)

        # Anonymous should return unauthorized
        response = self.client.delete(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.delete(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should return forbidden
        response = self.organizer_client.delete(self.bank_info_api_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_choices(self):
        """
        Test getting data choices
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.bank_choices)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should get forbidden
        response = self.student_client.get(self.bank_choices)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should get the choices
        response = self.organizer_client.get(self.bank_choices)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, OrganizerBankInfo.get_choices())
