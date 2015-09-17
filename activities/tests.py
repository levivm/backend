# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
import json
import tempfile

from PIL import Image
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http.request import HttpRequest
from django.contrib.auth.models import Permission
from django.utils.timezone import now
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from rest_framework import status
from utils.models import CeleryTask
from activities.models import Activity, ActivityPhoto, Tags, Chronogram,ActivityStockPhoto,SubCategory
from activities.serializers import ActivitiesSerializer, ChronogramsSerializer, ActivityPhotosSerializer
from activities.tasks import SendEmailChronogramTask, SendEmailLocationTask
from activities.views import ActivitiesViewSet, ChronogramsViewSet, ActivityPhotosViewSet, TagsViewSet, \
    ActivitiesSearchView
from utils.tests import BaseViewTest, BaseAPITestCase


class ActivitiesListViewTest(BaseViewTest):
    url = '/api/activities'
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
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
        request.data = request.DATA = data
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
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
    view = ChronogramsViewSet

    def _get_data_to_create_a_chronogram(self):
        now_unix_timestamp = int(now().timestamp())*1000
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
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_a_chronogram(self):
        organizer = self.get_organizer_client()
        data = json.dumps(self._get_data_to_create_a_chronogram())
        response = organizer.post(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(b'"session_price":123000', response.content)

    def test_other_organizer_shouldnt_create_a_chronogram(self):
        organizer = self.get_organizer_client(self.ANOTHER_ORGANIZER_ID)        
        data = json.dumps(self._get_data_to_create_a_chronogram())
        response = organizer.post(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_organizer_permissions_of_chronogram(self):
        request = HttpRequest()
        request.user = User.objects.get(id=self.ORGANIZER_ID)
        request.data = request.DATA = self._get_data_to_create_a_chronogram()
        serializer = ChronogramsSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        chronogram = serializer.create(validated_data=serializer.validated_data)
        self.assertTrue(request.user.has_perm('activities.add_chronogram'))
        self.assertTrue(request.user.has_perm('activities.change_chronogram', chronogram))
        self.assertTrue(request.user.has_perm('activities.delete_chronogram', chronogram))


class GetCalendarByActivityViewTest(BaseViewTest):
    view = ChronogramsViewSet
    CHRONOGRAM_ID = 1

    def __init__(self, methodName='runTest'):
        super(GetCalendarByActivityViewTest, self).__init__(methodName)
        self.url = '/api/activities/1/calendars/%s' % self.CHRONOGRAM_ID

    def _get_data_to_create_a_chronogram(self):
        now_unix_timestamp = int(now().timestamp())*1000
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
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        # self.method_should_be(clients=organizer, method='delete', status=status.HTTP_204_NO_CONTENT)

    def test_organizer_should_update_the_chronogram(self):
        organizer = self.get_organizer_client()
        data = self._get_data_to_create_a_chronogram()
        data.update({'session_price': 100000})
        data = json.dumps(data)
        response = organizer.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"session_price":100000', response.content)

    def test_organizer_shouldnt_delete_chronogram_if_has_students(self):
        organizer = self.get_organizer_client()
        chronogram = Chronogram.objects.get(id=self.CHRONOGRAM_ID)
        self.assertTrue(chronogram.orders.count() > 0)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_400_BAD_REQUEST)

    def test_organizer_should_delete_chronogram_if_hasnt_students(self):
        organizer = self.get_organizer_client()
        chronogram = Chronogram.objects.get(id=self.CHRONOGRAM_ID)
        chronogram.orders.all().delete()
        self.assertTrue(chronogram.orders.count() == 0)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_204_NO_CONTENT)

    def test_another_organizer_shouldnt_udpate_the_chronogram(self):
        organizer = self.get_organizer_client(self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_another_organizer_shouldnt_delete_the_chronogram(self):
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
        self.method_should_be(clients=self.client, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
        self.method_should_be(clients=self.client, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
        permission = Permission.objects.get_by_natural_key('add_activityphoto',\
                            'activities', 'activityphoto')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)

        permission = Permission.objects.get_by_natural_key('delete_activityphoto',\
                            'activities', 'activityphoto')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)


        permission = Permission.objects.get_by_natural_key('change_activity',\
                            'activities', 'activity')
        permission.user_set.add(self.organizer.user, self.another_organizer.user)


        assign_perm('activities.change_activity', \
                    user_or_group=self.organizer.user, obj=self.activity)

        assign_perm('activities.change_activity', \
                    user_or_group=self.organizer.user, obj=self.another_activity)


    def setUp(self):

        super(ActivityGalleryAPITest, self).setUp()

        settings.CELERY_ALWAYS_EAGER = True


        #Objects
        self.another_activity = mommy.make(Activity, organizer=self.organizer, \
                                   published=True,score=4.8)
        self.activity = mommy.make(Activity, organizer=self.organizer, \
                                   published=True)

        self.sub_category = mommy.make(SubCategory)
        self.activity_stock_photo = mommy.make(ActivityStockPhoto,\
                sub_category=self.sub_category)
        self.activity_photo = mommy.make(ActivityPhoto,activity=self.another_activity)



        # Methods data
        self.set_from_cover_post = {'cover_id':self.activity_stock_photo.id}

        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        self.tmp_file = tmp_file        

        #URLs
        self.set_cover_from_stock_url = reverse('set_cover_from_stock', \
                kwargs={'activity_pk': self.activity.id})

        self.upload_activity_photo_url = reverse('upload_activity_photo', \
                kwargs={'activity_pk': self.activity.id})

        self.delete_activity_photo_url = reverse('delete_activity_photo', \
                kwargs={'activity_pk': self.another_activity.id,
                        'gallery_pk':self.activity_photo.id})


        # Counters
        self.activity_photos_count = ActivityPhoto.objects.count()

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_create(self):
        """
        Test to upload an Activity Photo [POST]
        """

        organizer = self.organizer_client

        #Set permissions 
        self._set_permissions()


        # Anonymous should return unauthorized
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.client.post(self.upload_activity_photo_url , \
                                 {'photo':fp,'main_photo':False})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(), self.activity_photos_count)

        # Student should return forbidden
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.student_client.post(self.upload_activity_photo_url , \
                                 {'photo':fp,'main_photo':False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),\
                         self.activity_photos_count)


        # Organizer should not create a photo if he is not activity owner
        with open(self.tmp_file.name, 'rb') as fp:
            response = self.another_organizer_client.post(\
                       self.upload_activity_photo_url ,
                                 {'photo':fp,'main_photo':False})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # Organizer should create a photo from existing stock
        # and activity score should be updated

        self.assertEqual(self.activity.score, 0)

        with open(self.tmp_file.name, 'rb') as fp:
            response = organizer.post(self.upload_activity_photo_url , \
                                 {'photo':fp,'main_photo':False})

        activity_photo = ActivityPhoto.objects.latest('pk')
        expected_id = bytes('"id":%s' % activity_photo.id, 'utf8')

        expected_filename = bytes('%s' % \
                        activity_photo.photo.name.split('/')[-1], 'utf8')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected_id, response.content)
        self.assertIn(expected_filename, response.content)
        self.assertEqual(ActivityPhoto.objects.count(),\
                         self.activity_photos_count + 1)
        self.assertEqual(Activity.objects.latest('pk').score, 4.8)
        self.assertTrue(self.organizer.user.has_perm(\
                perm='activities.delete_activityphoto', obj=activity_photo))



    def test_create_from_stock(self):
        """
        Test to create an Activity Photo from stock [POST]
        """

        organizer = self.organizer_client

        #Set permissions 
        self._set_permissions()

        # Anonymous should return unauthorized
        response = self.client.post(self.set_cover_from_stock_url, \
                                    self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(), \
                    self.activity_photos_count)

        # Student should return forbidden
        response = self.student_client.post(self.set_cover_from_stock_url,\
                                            self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(),\
                         self.activity_photos_count)



        # Organizer should not create a photo if he is not activity owner
        response = self.another_organizer_client.post(\
                                self.set_cover_from_stock_url , \
                                self.set_from_cover_post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


        # Organizer should create a photo from existing stock
        response = organizer.post(self.set_cover_from_stock_url , \
                                 self.set_from_cover_post)
        stock_photo  = ActivityStockPhoto.objects.latest('pk')
        expected_filename = bytes('%s' % \
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

        #Set permissions
        self._set_permissions()
        assign_perm('activities.delete_activityphoto', \
            user_or_group=self.organizer.user, obj=self.activity_photo)


        # Anonymous should return unauthorized
        response = self.client.post(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ActivityPhoto.objects.count(), \
                self.activity_photos_count)



        # Student should return forbidden
        response = self.student_client.post(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(), \
                    self.activity_photos_count)


        # Organizer should not delete a photo if he is not activity owner
        response = self.another_organizer_client.post(\
                                self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(ActivityPhoto.objects.count(), \
                    self.activity_photos_count)


        # Organizer should delete a photo from his activity
        self.assertEqual(self.another_activity.score, 4.8)
        response = organizer.delete(self.delete_activity_photo_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ActivityPhoto.objects.count(),\
                         self.activity_photos_count - 1)
        self.assertEqual(Activity.objects.get(\
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
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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
            'point': [1, 2],
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
        self.method_should_be(clients=self.client, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=self.client, method='post', status=status.HTTP_401_UNAUTHORIZED)
        self.method_should_be(clients=self.client, method='put', status=status.HTTP_401_UNAUTHORIZED)
        self.method_should_be(clients=self.client, method='delete', status=status.HTTP_401_UNAUTHORIZED)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
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


class SendEmailChronogramTaskTest(BaseViewTest):
    CHRONOGRAM_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailChronogramTask()
        result = task.apply((self.CHRONOGRAM_ID, ))
        self.assertEqual(result.result, 'Task scheduled')

    def test_ignore_task_if_there_is_a_pending_task(self):
        task = SendEmailChronogramTask()
        task.apply((self.CHRONOGRAM_ID, False), countdown=60)
        task2 = SendEmailChronogramTask()
        result = task2.apply((self.CHRONOGRAM_ID, False))
        self.assertEqual(result.result, None)

    def test_task_should_delete_on_success(self):
        task = SendEmailChronogramTask()
        task.apply((self.CHRONOGRAM_ID, ), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 0)

    def test_email_task_should_create_if_has_students(self):
        chronogram = Chronogram.objects.get(id=self.CHRONOGRAM_ID)
        self.assertTrue(chronogram.orders.count() > 0)
        task = SendEmailChronogramTask()
        task.apply((self.CHRONOGRAM_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 1)

    def test_email_task_shouldnt_create_if_hasnt_students(self):
        chronogram = Chronogram.objects.get(id=self.CHRONOGRAM_ID)
        chronogram.orders.all().delete()
        self.assertEqual(chronogram.orders.count(), 0)
        task = SendEmailChronogramTask()
        task.apply((self.CHRONOGRAM_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 0)


class SendEmailLocationTaskTest(BaseViewTest):
    ACTIVITY_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailLocationTask()
        result = task.apply((self.ACTIVITY_ID, ),)
        self.assertEqual(result.result, 'Task scheduled')

    def test_ignore_task_if_there_is_a_pending_task(self):        
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False), countdown=60)
        task2 = SendEmailLocationTask()
        result = task2.apply((self.ACTIVITY_ID, False))
        self.assertEqual(result.result, None)

    def test_task_should_delete_on_success(self):
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, ))
        self.assertEqual(CeleryTask.objects.count(), 0)

    def test_email_task_should_create_if_has_students(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        orders = [order for chronogram in activity.chronograms.all() for order in chronogram.orders.all()]
        self.assertGreater(len(orders), 0)
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False), countdown=60)
        self.assertEqual(CeleryTask.objects.count(), 1)

    def test_email_task_shouldnt_create_if_hasnt_students(self):
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        [chronogram.orders.all().delete() for chronogram in activity.chronograms.all()]
        orders = [order for chronogram in activity.chronograms.all() for order in chronogram.orders.all()]
        self.assertEqual(len(orders), 0)
        task = SendEmailLocationTask()
        task.apply((self.ACTIVITY_ID, False))
        self.assertEqual(CeleryTask.objects.count(), 0)


class SearchActivitiesViewTest(BaseViewTest):
    url = '/api/activities/search'
    view = ActivitiesSearchView
    ACTIVITY_ID = 1


    def _get_activities_ordered(self, queryset=Activity.objects.all()):
        return queryset.annotate(number_assistants=Count('chronograms__orders__assistants'))\
            .order_by('number_assistants', 'chronograms__initial_date')

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_search_query(self):
        response = self.client.get(self.url, data={'q': 'curso de yoga', 'city': 1})
        activity = Activity.objects.filter(id=self.ACTIVITY_ID)
        serializer = ActivitiesSerializer(activity, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)


    def test_search_query_organizer_name(self):
        response = self.client.get(self.url, data={'q': 'XFDG', 'city': 1})
        activities = self._get_activities_ordered()
        serializer = ActivitiesSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_category(self):
        response = self.client.get(self.url, data={'category': 1, 'city': 1})
        activities = self._get_activities_ordered()
        serializer = ActivitiesSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, serializer.data)
        self.assertEqual(response.data, serializer.data)

    def test_search_subcategory(self):
        response = self.client.get(self.url, data={'subcategory': 1  , 'city': 1})
        activity = Activity.objects.filter(id=self.ACTIVITY_ID)
        serializer = ActivitiesSerializer(activity, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data, serializer.data)
        self.assertEqual(response.data, serializer.data)

    def test_search_date(self):
        response = self.client.get(self.url, data={'date': 1420123380601, 'city': 1})
        activity = Activity.objects.filter(id=self.ACTIVITY_ID)
        serializer = ActivitiesSerializer(activity, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_tags(self):
        response = self.client.get(self.url, data={'q': 'fitness', 'city': 1})
        activity = Activity.objects.filter(id=2)
        serializer = ActivitiesSerializer(activity, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_city(self):
        response = self.client.get(self.url, data={'city': 1})
        activities = self._get_activities_ordered()
        serializer = ActivitiesSerializer(activities, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_price_rage(self):
        data = {
            'cost_start':10000.0,
            'cost_end':20000,
        }
        response = self.client.get(self.url, data=data)
        activity = Activity.objects.filter(id=3)
        serializer = ActivitiesSerializer(activity,many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_level(self):
        response = self.client.get(self.url, data={'level':'I'})
        activity = Activity.objects.filter(id=self.ACTIVITY_ID)
        serializer = ActivitiesSerializer(activity,many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_certification(self):
        response = self.client.get(self.url, data={'certification':False})
        activities = self._get_activities_ordered()
        serializer = ActivitiesSerializer(activities,many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_weekends(self):

        response = self.client.get(self.url, data={'weekends':True})
        print(len(response.data))
        activity = Activity.objects.filter(id=self.ACTIVITY_ID)
        serializer = ActivitiesSerializer(activity,many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_search_empty(self):
        response = self.client.get(self.url, data={'q': 'empty', 'city': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])



class SubCategoriesViewTest(BaseAPITestCase):

    
    def setUp(self):
        super(SubCategoriesViewTest, self).setUp()

        # Objects
        self.sub_category = mommy.make(SubCategory, name='Yoga')
        self.activity_stock_photos = mommy.make(ActivityStockPhoto,\
                sub_category=self.sub_category,\
                _quantity=settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS)

        # URLs
        self.get_covers_url = reverse('get_covers_photos', \
            kwargs={'subcategory_id': self.sub_category.id})



    def test_get_covers_photos_from_subcategory(self):
        """
        Test get covers photos by given SubCategory
        """

        response = self.client.get(self.get_covers_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'photos', response.content)
        self.assertEqual(settings.MAX_ACTIVITY_POOL_STOCK_PHOTOS, \
                        len(response.data.get('photos')))
