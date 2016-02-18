# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
import datetime
import json
import tempfile
import time
import mock
from datetime import timedelta
from itertools import cycle

import factory
from PIL import Image
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http.request import HttpRequest
from django.utils.timezone import now, utc
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from rest_framework import status

from activities import constants
from activities.factories import ActivityFactory, SubCategoryFactory, CalendarFactory, TagsFactory
from activities.models import Activity, ActivityPhoto, Tags, Calendar, ActivityStockPhoto, \
    SubCategory
from activities.models import Category
from activities.serializers import ActivitiesSerializer, CalendarSerializer, \
    ActivitiesCardSerializer
from activities.tasks import SendEmailCalendarTask, SendEmailLocationTask
from activities.views import ActivitiesViewSet, CalendarViewSet, TagsViewSet
from locations.factories import CityFactory, LocationFactory
from orders.models import Assistant
from organizers.factories import OrganizerFactory
from organizers.models import Organizer
from utils.models import CeleryTask, EmailTaskRecord
from utils.tests import BaseViewTest, BaseAPITestCase


class ActivitiesListViewTest(BaseViewTest):
    url = '/api/activities/'
    view = ActivitiesViewSet

    def _get_data_to_create_an_activity(self):
        return {
            'sub_category': 1,
            'level': 'P',
            'short_description': "Descripci\u00f3n corta",
            'title': 'Curso de Test',
            'category': 1,
            'tags': ['test', 'drive', 'development'],
        }

    def test_url_should_resolve_correctly(self):
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
        self.method_should_be(clients=organizer, method='put',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_create_an_activity(self):
        organizer = self.get_organizer_client()
        data = json.dumps(self._get_data_to_create_an_activity())
        response = organizer.post(self.url, data=data, content_type='application/json')
        activity = Activity.objects.latest('pk')
        serializer = ActivitiesSerializer(activity)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data['score'], 0)

    def test_organizer_permissions_of_activity(self):
        data = self._get_data_to_create_an_activity()
        user = User.objects.get(id=self.ORGANIZER_ID)
        request = HttpRequest()
        request.user = user
        request.data = request.data = data
        serializer = ActivitiesSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        activity = serializer.create(validated_data=serializer.validated_data)
        self.assertTrue(user.has_perm('activities.add_activity'))
        self.assertTrue(user.has_perm('activities.change_activity', activity))
        self.assertFalse(user.has_perm('activities.delete_activity', activity))


class GetActivityViewTest(BaseViewTest):
    view = ActivitiesViewSet
    ACTIVITY_ID = 1

    def __init__(self, methodName='runTest'):
        super(GetActivityViewTest, self).__init__(methodName)
        self.url = '/api/activities/%s' % self.ACTIVITY_ID

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_url_should_resolve_correctly(self):
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
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_update_the_activity(self):
        organizer = self.get_organizer_client()
        data = json.dumps({'short_description': 'Otra descripcion corta'})
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        self.assertEqual(activity.score, 0)
        response = organizer.put(self.url, data=data, content_type='application/json')
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        self.assertEqual(activity.score, 100.0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"short_description":"Otra descripcion corta"', response.content)

    def test_another_organizer_shouldnt_update_the_activity(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CalendarsByActivityViewTest(BaseViewTest):
    url = '/api/activities/1/calendars'
    view = CalendarViewSet

    def _get_data_to_create_a_calendar(self):
        now_unix_timestamp = int(now().timestamp()) * 1000
        return {
            'initial_date': now_unix_timestamp,
            'number_of_sessions': 1,
            'capacity': 10,
            'activity': 1,
            'closing_sale': now_unix_timestamp,
            'session_price': 123000,
            'sessions': [{
                'date': now_unix_timestamp,
                'start_time': now_unix_timestamp,
                'end_time': now_unix_timestamp + 100000,
            }]
        }

    def test_url_should_resolve_correctly(self):
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
        self.method_should_be(clients=organizer, method='put',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_a_calendar(self):
        organizer = self.get_organizer_client()
        data = json.dumps(self._get_data_to_create_a_calendar())
        response = organizer.post(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'"session_price":123000', response.content)

    def test_other_organizer_shouldnt_create_a_calendar(self):
        organizer = self.get_organizer_client(self.ANOTHER_ORGANIZER_ID)
        data = json.dumps(self._get_data_to_create_a_calendar())
        response = organizer.post(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_permissions_of_calendar(self):
        request = HttpRequest()
        request.user = User.objects.get(id=self.ORGANIZER_ID)
        request.data = request.data = self._get_data_to_create_a_calendar()
        serializer = CalendarSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        calendar = serializer.create(validated_data=serializer.validated_data)
        self.assertTrue(request.user.has_perm('activities.add_calendar'))
        self.assertTrue(request.user.has_perm('activities.change_calendar', calendar))
        self.assertTrue(request.user.has_perm('activities.delete_calendar', calendar))


class GetCalendarByActivityViewTest(BaseViewTest):
    view = CalendarViewSet
    CALENDAR_ID = 1

    def __init__(self, methodName='runTest'):
        super(GetCalendarByActivityViewTest, self).__init__(methodName)
        self.url = '/api/activities/1/calendars/%s' % self.CALENDAR_ID

    def _get_data_to_create_a_calendar(self):
        now_unix_timestamp = int(now().timestamp()) * 1000
        return {
            'initial_date': now_unix_timestamp,
            'number_of_sessions': 1,
            'capacity': 10,
            'activity': 1,
            'closing_sale': now_unix_timestamp,
            'session_price': 123000,
            'sessions': [{
                'date': now_unix_timestamp,
                'start_time': now_unix_timestamp,
                'end_time': now_unix_timestamp + 100000,
            }]
        }

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_url_should_resolve_correctly(self):
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
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # self.method_should_be(clients=organizer, method='delete', status=status.HTTP_204_NO_CONTENT)

    def test_organizer_should_update_the_calendar(self):
        organizer = self.get_organizer_client()
        calendar = Calendar.objects.get(id=self.CALENDAR_ID)
        data = self._get_data_to_create_a_calendar()
        data.update({'capacity': 20, 'session_price': calendar.session_price})
        data = json.dumps(data)
        response = organizer.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.content)
        self.assertIn(b'"capacity":20', response.content)

    def test_organizer_shouldnt_delete_calendar_if_has_students(self):
        organizer = self.get_organizer_client()
        calendar = Calendar.objects.get(id=self.CALENDAR_ID)
        self.assertTrue(calendar.orders.count() > 0)
        self.method_should_be(clients=organizer, method='delete',
                              status=status.HTTP_400_BAD_REQUEST)

    def test_organizer_should_delete_calendar_if_hasnt_students(self):
        organizer = self.get_organizer_client()
        calendar = Calendar.objects.get(id=self.CALENDAR_ID)
        calendar.orders.all().delete()
        self.assertTrue(calendar.orders.count() == 0)
        self.method_should_be(clients=organizer, method='delete',
                              status=status.HTTP_204_NO_CONTENT)

    def test_another_organizer_shouldnt_udpate_the_calendar(self):
        organizer = self.get_organizer_client(self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_another_organizer_shouldnt_delete_the_calendar(self):
        organizer = self.get_organizer_client(self.ANOTHER_ORGANIZER_ID)
        response = organizer.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PublishActivityViewTest(BaseViewTest):
    ACTIVITY_ID = 1
    view = ActivitiesViewSet

    def __init__(self, *args, **kwargs):
        super(PublishActivityViewTest, self).__init__(*args, **kwargs)
        self.url = '/api/activities/%s/publish' % self.ACTIVITY_ID

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_should_be(clients=self.client, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_publish_the_activity(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        activity.published = False
        self.assertFalse(activity.published)
        organizer = self.get_organizer_client()
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        self.assertTrue(activity.published)

    def test_another_organizer_shouldnt_publish_the_activity(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class UnpublishActivityViewTest(BaseViewTest):
    ACTIVITY_ID = 1
    view = ActivitiesViewSet

    def __init__(self, *args, **kwargs):
        super(UnpublishActivityViewTest, self).__init__(*args, **kwargs)
        self.url = '/api/activities/%s/unpublish' % self.ACTIVITY_ID

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_should_be(clients=self.client, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_unpublish_the_activity(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        activity.published = True
        self.assertTrue(activity.published)
        organizer = self.get_organizer_client()
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        self.assertFalse(activity.published)

    def test_another_organizer_shouldnt_unpublish_the_activity(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class ActivityGalleryAPITest(BaseAPITestCase):
    def _set_permissions(self):
        # Set permissions
        permission = Permission.objects.get_by_natural_key('add_activityphoto',
                                                           'activities', 'activityphoto')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)

        permission = Permission.objects.get_by_natural_key('delete_activityphoto',
                                                           'activities', 'activityphoto')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)

        permission = Permission.objects.get_by_natural_key('change_activity',
                                                           'activities', 'activity')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)

        assign_perm('activities.change_activity',
                    user_or_group=self.organizer.user, obj=self.activity)

        assign_perm('activities.change_activity',
                    user_or_group=self.organizer.user, obj=self.another_activity)

    def setUp(self):
        super(ActivityGalleryAPITest, self).setUp()

        settings.CELERY_ALWAYS_EAGER = True

        # Objects
        self.another_activity = mommy.make(Activity, organizer=self.organizer,
                                           published=True, score=4.8)
        self.activity = mommy.make(Activity, organizer=self.organizer,
                                   published=True)

        self.sub_category = mommy.make(SubCategory)
        self.activity_stock_photo = mommy.make(ActivityStockPhoto,
                                               sub_category=self.sub_category)
        self.activity_photo = mommy.make(ActivityPhoto, activity=self.another_activity)

        # Methods data
        self.set_from_cover_post = {'cover_id': self.activity_stock_photo.id}

        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, format='JPEG')
        self.tmp_file = tmp_file

        # URLs
        self.set_cover_from_stock_url = reverse('activities:set_cover_from_stock',
                                                kwargs={'activity_pk': self.activity.id})

        self.upload_activity_photo_url = reverse('activities:upload_activity_photo',
                                                 kwargs={'activity_pk': self.activity.id})

        self.delete_activity_photo_url = reverse('activities:delete_activity_photo',
                                                 kwargs={'activity_pk': self.another_activity.id,
                                                         'gallery_pk': self.activity_photo.id})

        # Counters
        self.activity_photos_count = ActivityPhoto.objects.count()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create(self):
        """
        Test to upload an Activity Photo [POST]
        """

        organizer = self.organizer_client

        # Set permissions
        self._set_permissions()

        # Anonymous should return unauthorized
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.client.post(self.upload_activity_photo_url,
                                        {'photo': fp, 'main_photo': False})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(), self.activity_photos_count)

        # Student should return forbidden
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.student_client.post(self.upload_activity_photo_url,
                                                {'photo': fp, 'main_photo': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Organizer should not create a photo if he is not activity owner
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.another_organizer_client.post(
                    self.upload_activity_photo_url,
                    {'photo': fp, 'main_photo': False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should create a photo from existing stock
        # and activity score should be updated

        self.assertEqual(self.activity.score, 0)

        with open(self.tmp_file.name, 'rb') as fp:
            response = organizer.post(self.upload_activity_photo_url,
                                      {'photo': fp, 'main_photo': False})

        activity_photo = ActivityPhoto.objects.latest('pk')
        expected_id = bytes('"id":%s' % activity_photo.id, 'utf8')

        expected_filename = bytes('%s' %
                                  activity_photo.photo.name.split('/')[-1], 'utf8')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected_id, response.content)
        self.assertIn(expected_filename, response.content)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count + 1)
        self.assertEqual(Activity.objects.latest('pk').score, 4.8)
        self.assertTrue(self.organizer.user.has_perm(
                perm='activities.delete_activityphoto', obj=activity_photo))

    def test_create_from_stock(self):
        """
        Test to create an Activity Photo from stock [POST]
        """

        organizer = self.organizer_client

        # Set permissions
        self._set_permissions()

        # Anonymous should return unauthorized
        response = self.client.post(self.set_cover_from_stock_url,
                                    self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Student should return forbidden
        response = self.student_client.post(self.set_cover_from_stock_url,
                                            self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Organizer should not create a photo if he is not activity owner
        response = self.another_organizer_client.post(
                self.set_cover_from_stock_url,
                self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should create a photo from existing stock
        response = organizer.post(self.set_cover_from_stock_url,
                                  self.set_from_cover_post)
        stock_photo = ActivityStockPhoto.objects.latest('pk')
        expected_filename = bytes('%s' %
                                  stock_photo.photo.name.split('/')[-1], 'utf8')

        activity_photo = ActivityPhoto.objects.latest('pk')
        expected_id = bytes('"id":%s' % activity_photo.id, 'utf8')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected_id, response.content)
        self.assertIn(expected_filename, response.content)

    def test_delete(self):
        """
        Test to delete a Activity Photo [POST]
        """

        organizer = self.organizer_client

        # Set permissions
        self._set_permissions()
        assign_perm('activities.delete_activityphoto',
                    user_or_group=self.organizer.user, obj=self.activity_photo)

        # Anonymous should return unauthorized
        response = self.client.post(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Student should return forbidden
        response = self.student_client.post(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Organizer should not delete a photo if he is not activity owner
        response = self.another_organizer_client.post(
                self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count)

        # Organizer should delete a photo from his activity
        self.assertEqual(self.another_activity.score, 4.8)
        response = organizer.delete(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ActivityPhoto.objects.count(),
                         self.activity_photos_count - 1)
        self.assertEqual(Activity.objects.get(
                id=self.another_activity.id).score, 0.0)


class ActivityInfoViewTest(BaseViewTest):
    url = '/api/activities/info'
    view = ActivitiesViewSet

    def test_url_should_resolve_correctly(self):
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
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


class ActivityTagsViewTest(BaseViewTest):
    url = '/api/activities/tags'
    view = TagsViewSet
    response_data = b'"name":"yoga"'

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client, response_data=self.response_data)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student, response_data=self.response_data)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer, response_data=self.response_data)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_create_a_tag(self):
        organizer = self.get_organizer_client()
        data = json.dumps({'name': 'another tag'})
        response = organizer.post(self.url, data=data, content_type='application/json')
        tag = Tags.objects.latest('pk')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tag.name, 'another tag')
        self.assertIn(b'another tag', response.content)


class UpdateActivityLocationViewTest(BaseViewTest):
    view = ActivitiesViewSet
    ACTIVITY_ID = 1

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.url = '/api/activities/%s/locations' % self.ACTIVITY_ID

    def get_data_to_update(self):
        return {
            'point': [4, -74],
            'address': 'Calle falsa 123',
            'city': 1
        }

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_should_be(clients=self.client, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=self.client, method='post',
                              status=status.HTTP_401_UNAUTHORIZED)
        self.method_should_be(clients=self.client, method='put',
                              status=status.HTTP_401_UNAUTHORIZED)
        self.method_should_be(clients=self.client, method='delete',
                              status=status.HTTP_401_UNAUTHORIZED)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post',
                              status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_update_location(self):
        organizer = self.get_organizer_client()
        data = json.dumps(self.get_data_to_update())
        response = organizer.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'Calle falsa 123', response.content)

    def test_another_organizer_shouldnt_update_location(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class SendEmailCalendarTaskTest(BaseViewTest):
    CALENDAR_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailCalendarTask()
        result = task.apply((self.CALENDAR_ID,))
        self.assertEqual(result.result, 'Task scheduled')

    def test_ignore_task_if_there_is_a_pending_task(self):
        task = SendEmailCalendarTask()
        task.apply((self.CALENDAR_ID, False), countdown=60)
        task2 = SendEmailCalendarTask()
        result = task2.apply((self.CALENDAR_ID, False))
        self.assertEqual(result.result, None)

    def test_task_should_delete_on_success(self):
        task = SendEmailCalendarTask()
        task.apply((self.CALENDAR_ID,), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 0)

    def test_email_task_should_create_if_has_students(self):
        calendar = Calendar.objects.get(id=self.CALENDAR_ID)
        self.assertTrue(calendar.orders.count() > 0)
        task = SendEmailCalendarTask()
        task.apply((self.CALENDAR_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 1)

    def test_email_task_shouldnt_create_if_hasnt_students(self):
        calendar = Calendar.objects.get(id=self.CALENDAR_ID)
        calendar.orders.all().delete()
        self.assertEqual(calendar.orders.count(), 0)
        task = SendEmailCalendarTask()
        task.apply((self.CALENDAR_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 0)


class SendEmailLocationTaskTest(BaseViewTest):
    ACTIVITY_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailLocationTask()
        result = task.apply((self.ACTIVITY_ID,), )
        self.assertEqual(result.result, 'Task scheduled')

    def test_ignore_task_if_there_is_a_pending_task(self):
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False), countdown=60)
        task2 = SendEmailLocationTask()
        result = task2.apply((self.ACTIVITY_ID, False))
        self.assertEqual(result.result, None)

    def test_task_should_delete_on_success(self):
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID,))
        self.assertEqual(CeleryTask.objects.count(), 0)

    def test_email_task_should_create_if_has_students(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        orders = [order for calendar in activity.calendars.all() for order in
                  calendar.orders.all()]
        self.assertGreater(len(orders), 0)
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 1)

    def test_email_task_shouldnt_create_if_hasnt_students(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        [calendar.orders.all().delete() for calendar in activity.calendars.all()]
        orders = [order for calendar in activity.calendars.all() for order in
                  calendar.orders.all()]
        self.assertEqual(len(orders), 0)
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False))
        self.assertEqual(CeleryTask.objects.count(), 0)


class SearchActivitiesViewTest(BaseAPITestCase):
    def _get_activities_ordered(self, queryset=Activity.objects.all(), order_by=None):
        order = order_by or ('-score',)
        return queryset.order_by(*order)

    def unique(self, array):
        seen = list()
        for item in array:
            if item not in seen:
                seen.append(item)
                yield item

    def setUp(self):
        super(SearchActivitiesViewTest, self).setUp()

        self.query_keyword = 'yoga'
        self.organizer_name = 'buckridge'
        self.now = now()
        self.tag_name = 'fitness'
        self.city = CityFactory()
        self.location = LocationFactory(city=self.city)
        self.price = 100000

        self.organizer = OrganizerFactory(name='%s Group' % self.organizer_name.capitalize())
        self.subcategory = SubCategoryFactory()
        self.activities = self.create_activities()
        self.url = reverse('activities:search')

    def create_activities(self):
        tag = TagsFactory(name=self.tag_name)
        titles = ['%s de %s' % (t, self.query_keyword.capitalize()) for t in ['Clases', 'Curso']]
        activities = ActivityFactory.create_batch(2, title=factory.Iterator(titles),
                                                  location__city=self.city,
                                                  level=constants.LEVEL_P, published=True)
        activities.append(ActivityFactory(title='Curso de Cocina', organizer=self.organizer,
                                          level=constants.LEVEL_I,
                                          published=True))
        activities.append(
            ActivityFactory(sub_category=self.subcategory, tags=[tag], level=constants.LEVEL_A,
                            certification=True, published=True))
        CalendarFactory(activity=activities[-1], initial_date=now() - timedelta(days=10),
                        session_price=self.price,
                        is_weekend=True)
        return activities

    def create_calendars(self):
        calendars = list()
        for i, activity in enumerate(self.activities):
            dates = [now() - timedelta(days=1), now(), now() + timedelta(days=2),
                     now() - timedelta(days=4)]
            price = (i + 1) * 100000
            calendars.append(mommy.make(Calendar, _quantity=4, activity=activity,
                                        session_price=price, initial_date=cycle(dates)))

        return [item for sublist in calendars for item in sublist]

    def create_assistants(self):
        for i, calendar in enumerate(self.calendars):
            quantity = i + 1
            mommy.make(Assistant, _quantity=quantity, order__calendar=calendar)

    def test_search_query(self):
        response = self.client.get(self.url, data={'q': 'curso de %s' % self.query_keyword})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(title__icontains=self.query_keyword))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_query_organizer_name(self):
        response = self.client.get(self.url, data={'q': self.organizer_name})
        activities = self._get_activities_ordered(
            Activity.objects.filter(organizer=self.organizer))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_category(self):
        response = self.client.get(self.url, data={'category': self.subcategory.category.id})
        activities = self._get_activities_ordered(
                queryset=Activity.objects.filter(sub_category__category=self.subcategory.category))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_subcategory(self):
        response = self.client.get(self.url, data={'subcategory': self.subcategory.id})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(sub_category=self.subcategory))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data['results'], serializer.data)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_date(self):
        date = int(time.mktime(self.now.timetuple()) * 1000)
        response = self.client.get(self.url, data={'date': date})
        activity = self._get_activities_ordered(
            queryset=Activity.objects.filter(calendars__initial_date__gte=self.now))
        serializer = ActivitiesCardSerializer(activity, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_tags(self):
        response = self.client.get(self.url, data={'q': self.tag_name})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(tags__name__icontains=self.tag_name))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_city(self):
        response = self.client.get(self.url, data={'city': self.city.id})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(location__city=self.city))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_price_range(self):
        data = {
            'cost_start': self.price,
            'cost_end': self.price + 100000,
        }
        response = self.client.get(self.url, data=data)
        activities = self._get_activities_ordered(
                queryset=Activity.objects.filter(
                    calendars__session_price__range=(self.price, self.price + 100000)))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_level(self):
        response = self.client.get(self.url, data={'level': 'I'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(level=constants.LEVEL_I))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_certification(self):
        response = self.client.get(self.url, data={'certification': 'false'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(certification=False))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_weekends(self):
        response = self.client.get(self.url, data={'weekends': 'true'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(calendars__is_weekend=True))
        serializer = ActivitiesCardSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_search_empty(self):
        response = self.client.get(self.url, data={'q': 'empty', 'city': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

    def test_pagination(self):
        scores = factory.Iterator(range(100))
        ActivityFactory.create_batch(50, location__city=self.city, published=True, score=scores)
        response = self.client.get(self.url, data={'city': self.city.id})
        activities = self._get_activities_ordered(
                queryset=Activity.objects.filter(location__city=self.city, published=True))
        serializer = ActivitiesCardSerializer(activities[:10], many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_min_price_order(self):
        self.create_calendars()
        response = self.client.get(self.url, data={'q': self.query_keyword, 'o': 'min_price'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(title__icontains=self.query_keyword),
            order_by=['calendars__session_price'])
        serializer = ActivitiesCardSerializer(self.unique(activities), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_max_price_order(self):
        self.create_calendars()
        response = self.client.get(self.url, data={'q': self.query_keyword, 'o': 'max_price'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(title__icontains=self.query_keyword),
            order_by=['-calendars__session_price'])
        serializer = ActivitiesCardSerializer(self.unique(activities), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_score_order(self):
        self.create_calendars()
        response = self.client.get(self.url, data={'q': self.query_keyword, 'o': 'score'})
        activities = self._get_activities_ordered(
            queryset=Activity.objects.filter(title__icontains=self.query_keyword),
            order_by=['-score'])
        serializer = ActivitiesCardSerializer(self.unique(activities), many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)

    def test_closest_order(self):
        data = {
            'cost_start': self.price,
            'cost_end': self.price + 100000,
            'q': self.query_keyword,
            'o': 'closest'
        }
        self.create_calendars()
        response = self.client.get(self.url, data=data)
        activities = Activity.objects.filter(title__icontains=self.query_keyword)
        unix_epoch = datetime.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
        activities = sorted(activities,
                            key=lambda
                                a: a.closest_calendar().initial_date if a.closest_calendar() else unix_epoch)
        request = mock.MagicMock()
        request.query_params = {
                'cost_start': self.price,
                'cost_end': self.price + 100000,
            }
        serializer = ActivitiesCardSerializer(activities, many=True,context={'request':request})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)


class SubCategoriesViewTest(BaseAPITestCase):
    def setUp(self):
        super(SubCategoriesViewTest, self).setUp()

        # Objects
        self.category = mommy.make(Category)
        self.sub_category = mommy.make(SubCategory, name='Yoga', category=self.category)
        self.another_sub_category = mommy.make(SubCategory, category=self.category)
        # sub_category stock photos
        mommy.make(ActivityStockPhoto,
                   sub_category=self.sub_category,
                   _quantity=settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS)

        # another_sub_category stock photos
        mommy.make(ActivityStockPhoto,
                   sub_category=self.another_sub_category,
                   _quantity=settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS - 1)

        # URLs
        self.get_covers_url = reverse('activities:get_covers_photos',
                                      kwargs={'subcategory_id': self.sub_category.id})

        self.get_covers_url_another_subcategory = reverse('activities:get_covers_photos',
                                                          kwargs={
                                                              'subcategory_id': self.another_sub_category.id})

    def test_get_covers_photos_from_subcategory_with_not_enough_pictures(self):
        """
        Test get covers photos by given SubCategory even when that SubCategory has not
        enough photos 
        """
        # Stock photo should returns settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS(number)
        # from stock even when given sub_category has not required amount of pictures
        response = self.client.get(self.get_covers_url_another_subcategory)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'pictures', response.content)
        self.assertEqual(settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS,
                         len(response.data.get('pictures')))

    def test_get_covers_photos_from_subcategory(self):
        """
        Test get covers photos by given SubCategory
        """

        # Stock photo should returns settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS(number)
        # photos from stock
        response = self.client.get(self.get_covers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'pictures', response.content)
        self.assertEqual(settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS,
                         len(response.data.get('pictures')))


class ShareActivityEmailViewTest(BaseAPITestCase):
    """
    Test to share an activity by email
    """

    def setUp(self):
        self.activity = mommy.make(Activity)

        # URLs
        self.share_url = reverse('activities:share_email_activity',
                                 kwargs={'activity_pk': self.activity.id})

        # Celery
        settings.CELERY_ALWAYS_EAGER = True

    def test_post(self):
        """
        Test the sending email
        """

        data = {
            'emails': 'email1@example.com, email2@example.com'
        }

        response = self.client.post(self.share_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for email in data['emails'].split(','):
            self.assertTrue(EmailTaskRecord.objects.filter(to=email.strip(), send=True).exists())

    def test_validation_emails(self):
        """
        Test validation emails
        """

        # Should be emails
        response = self.client.post(self.share_url, data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Should be well formed
        response = self.client.post(self.share_url, data={'emails': 'asdfa'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'Introduzca una dirección de correo electrónico válida')


class AutoCompleteViewTest(BaseAPITestCase):
    """
    Class to test the auto complete view
    """

    def setUp(self):
        # Arrangement
        self.categories = self.create_categories()
        self.subcategories = self.create_subcategories()
        self.tags = self.create_tags()
        self.organizers = self.create_organizers()
        self.activities = self.create_activities()

        # URL
        self.auto_complete_url = reverse('activities:auto_complete')

    def test_read(self):
        """
        Test the result of the autocomplete
        """

        contains = ['danza', 'deportes', 'documentales', 'derecho', 'docencia',
                    'deportes de colombia']

        # Should response the contains data
        response = self.client.get(self.auto_complete_url, {'q': 'd'})
        self.assertEqual(len(response.data), len(contains))
        self.assertTrue(all(item in response.data for item in contains))

        # Should response empty data
        response = self.client.get(self.auto_complete_url)
        self.assertListEqual(response.data, list())

    def create_categories(self):
        categories = mommy.make(Category, name='Derecho', _quantity=1)
        categories += mommy.make(Category, name='Arte', _quantity=1)
        return categories

    def create_subcategories(self):
        subcategories = mommy.make(SubCategory, name='Docencia', category=self.categories[0],
                                   _quantity=1)
        subcategories += mommy.make(SubCategory, name='Idiomas', category=self.categories[1],
                                    _quantity=1)
        subcategories += mommy.make(SubCategory, name='Otros', category=self.categories[0],
                                    _quantity=1)
        return subcategories

    def create_tags(self):
        tags = mommy.make(Tags, name='Deportes', _quantity=1)
        tags += mommy.make(Tags, name='Derecho', _quantity=1)
        tags += mommy.make(Tags, name='Documentales', _quantity=1)
        tags += mommy.make(Tags, name='Baile', _quantity=1)
        return tags

    def create_organizers(self):
        organizer = mommy.make(Organizer, name='Deportes de Colombia', _quantity=1)
        organizer += mommy.make(Organizer, name='Universidad de Bogotá', _quantity=1)
        return organizer

    def create_activities(self):
        activities = mommy.make(Activity, title='Yoga', sub_category=self.subcategories[0],
                                organizer=self.organizers[0], tags=[self.tags[0]], _quantity=1)
        activities += mommy.make(Activity, title='Danza', sub_category=self.subcategories[1],
                                 organizer=self.organizers[1], tags=[self.tags[1]], _quantity=1)
        return activities
