import json
import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.http.request import HttpRequest
from django.utils.timezone import now
from rest_framework import status

from activities.models import Activity, ActivityPhoto, Tags
from activities.serializers import ActivitiesSerializer, ChronogramsSerializer, ActivityPhotosSerializer
from activities.views import ActivitiesViewSet, ChronogramsViewSet, ActivityPhotosViewSet, TagsViewSet
from utils.tests import BaseViewTest


class ActivitiesListViewTest(BaseViewTest):
    url = '/api/activities'
    view = ActivitiesViewSet

    def _get_data_to_create_an_activity(self):
        return {
            'sub_category': 1,
            'level': 'P',
            'short_description': 'Descripción corta',
            'title': 'Curso de Test',
            'type': 'CU',
            'category': 1,
            'large_description': 'Descripción detallada',
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
        expected = bytes('"id":%s' % activity.id, 'utf8')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected, response.content)

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
        self.assertFalse(user.has_perm('activities.delete_activity'))


class GetActivityViewTest(BaseViewTest):
    url = '/api/activities/1'
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
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_update_the_activity(self):
        organizer = self.get_organizer_client()
        data = json.dumps({
            'large_description': 'Otra descripcion detallada'
        })
        response = organizer.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"large_description":"Otra descripcion detallada"', response.content)

    def test_another_organizer_shouldnt_update_the_activity(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.put(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class CalendarsByActivityViewTest(BaseViewTest):
    url = '/api/activities/1/calendars'
    view = ChronogramsViewSet

    def _get_data_to_create_a_chronogram(self):
        now_unix_timestamp = int(now().timestamp())
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
                'end_time': now_unix_timestamp + 1,
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
    url = '/api/activities/1/calendars/1'
    view = ChronogramsViewSet

    def _get_data_to_create_a_chronogram(self):
        now_unix_timestamp = int(now().timestamp())
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
                'end_time': now_unix_timestamp + 1,
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
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_204_NO_CONTENT)

    def test_organizer_should_update_the_chronogram(self):
        organizer = self.get_organizer_client()
        data = self._get_data_to_create_a_chronogram()
        data.update({'session_price': 100000})
        data = json.dumps(data)
        response = organizer.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"session_price":100000', response.content)

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


class ActivityGalleryViewTest(BaseViewTest):
    url = '/api/activities/1/gallery'
    view = ActivityPhotosViewSet

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_create_a_photo(self):
        organizer = self.get_organizer_client()
        image = Image.new('RGB', (100, 100), color='red')
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file)
        with open(tmp_file.name, 'rb') as fp:
            response = organizer.post(self.url, data={'photo': fp})
        activity_photo = ActivityPhoto.objects.latest('pk')
        expected_id = bytes('"id":%s' % activity_photo.id, 'utf8')
        expected_filename = bytes('%s' % tmp_file.name.split('/')[-1], 'utf8')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected_id, response.content)
        self.assertIn(expected_filename, response.content)

    def test_another_organizer_shouldnt_create_a_photo(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        response = organizer.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_organizer_with_photo(self):
        user = User.objects.get(id=self.ORGANIZER_ID)
        activity = Activity.objects.get(id=1)
        image = Image.new('RGB', (100, 100), color='red')
        imgfile = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(imgfile)
        with open(imgfile.name, 'rb') as fp:
             imagestring= fp.read()
        file = SimpleUploadedFile(imgfile.name, content=imagestring, content_type='image/jpeg')
        request = HttpRequest()
        request.user = user
        request.data = request.DATA = {'photo': file}
        request.FILES = {'photo': file}
        serializer = ActivityPhotosSerializer(data=request.data, context={'request': request, 'activity': activity})
        serializer.is_valid(raise_exception=True)
        activity_photo = serializer.create(validated_data=serializer.validated_data)
        self.assertTrue(request.user.has_perm('activities.add_activityphoto'))
        self.assertFalse(request.user.has_perm('activities.change_activityphoto', activity_photo))
        self.assertTrue(request.user.has_perm('activities.delete_activityphoto', activity_photo))


class GetActivityGalleryViewTest(BaseViewTest):
    url = '/api/activities/1/gallery/1'
    view = ActivityPhotosViewSet

    def test_url_should_resolve_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        another_organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_200_OK)
        self.method_should_be(clients=another_organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


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
