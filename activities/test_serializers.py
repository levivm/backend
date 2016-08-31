import mock
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory, ActivityFactory, SubCategoryFactory
from activities.models import Calendar, Activity
from activities.serializers import CalendarSerializer, CategoriesSerializer, ActivitiesSerializer
from locations.factories import LocationFactory
from orders.models import Assistant, Order
from orders.serializers import AssistantsSerializer
from organizers.factories import OrganizerFactory
from organizers.serializers import OrganizersSerializer
from utils.serializers import UnixEpochDateField
from . import constants as activities_constants


class CalendarSerializerTest(APITestCase):
    """
    Test cases for CalendarSerializer
    """

    def setUp(self):
        self.calendar = CalendarFactory(session_price=100000)
        self.order = mommy.make(Order, status=Order.ORDER_APPROVED_STATUS, calendar=self.calendar,
                                quantity=3)
        self.assistants = mommy.make(Assistant, order=self.order, _quantity=2)

    def test_read(self):
        """
        Test the serialize data
        """
        epoch = UnixEpochDateField()

        mommy.make(Assistant, order=self.order, enrolled=False)
        serializer = CalendarSerializer(self.calendar)

        content = {
            'id': self.calendar.id,
            'activity': self.calendar.activity.id,
            'initial_date': epoch.to_representation(self.calendar.initial_date),
            'enroll_open': True,
            'session_price': self.calendar.session_price,
            'schedules': '<p><strong>Lunes - Viernes</strong></p><p>6:00pm - 9:00pm</p>',
            'assistants': AssistantsSerializer(self.calendar.get_assistants(), many=True,
                                               remove_fields=['student']).data,
            'is_weekend': self.calendar.is_weekend,
            'is_free': self.calendar.is_free,
            'available_capacity': self.calendar.available_capacity,

        }
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    def test_create(self):
        """
        The serializer should create the calendar with the data passed
        """
        today = now()
        epoch = UnixEpochDateField()
        activity = ActivityFactory()
        data = {
            'activity': activity.id,
            'initial_date': epoch.to_representation(today),
            'session_price': 300000,
            'available_capacity': 10,
            'note': 'Note',
            'schedules': '<p><strong>Lunes - Viernes</strong></p><p>6:00pm - 9:00pm</p>',
        }

        calendar_counter = Calendar.objects.count()

        serializer = CalendarSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(Calendar.objects.count(), calendar_counter + 1)

    def test_should_not_update_schedule_if_there_are_orders(self):
        """
        The serializer shouldn't allow to update the schedules field
        if there are orders associated to the calendar
        """
        data = {'schedules': '<p>No Schedule!</p>'}
        msg = 'No se puede cambiar el horario debido a que existen ordenes relacionadas.'
        serializer = CalendarSerializer(self.calendar, data=data, partial=True)
        with self.assertRaisesMessage(ValidationError, "{'schedules': ['%s']}" % msg):
            serializer.is_valid(raise_exception=True)


class ActivitySerializerTest(APITestCase):
    """
    Test for ActivitySerializer
    """

    def setUp(self):
        self.activity = ActivityFactory()

    def test_read(self):
        """
        Test the serializer data
        """

        category_data = CategoriesSerializer(instance=self.activity.sub_category.category,
                                             remove_fields=['subcategories']).data
        # location_data = LocationsSerializer(self.activity.location).data
        organizer_data = OrganizersSerializer(self.activity.organizer).data

        content = {
            'id': self.activity.id,
            'title': self.activity.title,
            'short_description': self.activity.short_description,
            'sub_category': self.activity.sub_category.id,
            'sub_category_display': self.activity.sub_category.name,
            'level': self.activity.level,
            'level_display': self.activity.get_level_display(),
            'category': category_data,
            'content': self.activity.content,
            'requirements': self.activity.requirements,
            'return_policy': self.activity.return_policy,
            'extra_info': self.activity.extra_info,
            'audience': self.activity.audience,
            'goals': self.activity.goals,
            'methodology': self.activity.methodology,
            'youtube_video_url': self.activity.youtube_video_url,
            'published': self.activity.published,
            'certification': self.activity.certification,
            'calendars': [],
            'steps': activities_constants.ACTIVITY_STEPS,
            'organizer': organizer_data,
            'instructors': [],
            'score': self.activity.score,
            'rating': self.activity.rating,
            'is_open': False,
        }

        serializer = ActivitiesSerializer(self.activity)
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    def test_create(self):
        """
        Test the creation of the instance with the serializer
        """
        organizer = OrganizerFactory()

        data = {
            'sub_category': SubCategoryFactory().id,
            'organizer': organizer.id,
            'title': 'Clase de conducción',
            'short_description': 'Clase de conducción',
            'level': 'P',
            'goals': 'Conducir',
            'methodology': 'Por la derecha',
            'content': 'Poco la verdad',
            'audience': 'Ciegos y ancianos',
            'requirements': 'No saber conducir',
            'return_policy': 'Ninguna',
            'location': LocationFactory().id,
        }

        request = mock.MagicMock()
        request.user = organizer.user

        activities_counter = Activity.objects.count()
        serializer = ActivitiesSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(Activity.objects.count(), activities_counter + 1)

    def test_should_not_update_is_open_if_there_are_calendars(self):
        """
        The serializer should not allow update is_open if there is any calendar
        """
        activity = ActivityFactory()
        CalendarFactory(activity=activity)
        data = {'is_open': True}

        request = mock.MagicMock()
        request.user = activity.organizer.user

        serializer = ActivitiesSerializer(activity, data=data, partial=True,
                                          context={'request': request})
        msg = 'No se puede cambiar el tipo de horario porque existen calendarios relacionados.'
        with self.assertRaisesMessage(ValidationError, "{'is_open': ['%s']}" % msg):
            serializer.is_valid(raise_exception=True)
