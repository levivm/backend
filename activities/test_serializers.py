import mock
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory, ActivityFactory, SubCategoryFactory, \
    CalendarPackageFactory
from activities.models import Calendar, Activity, CalendarPackage
from activities.serializers import CalendarSerializer, CategoriesSerializer, ActivitiesSerializer, \
    CalendarPackageSerializer
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
        package = CalendarPackageFactory(calendar=self.calendar)
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
            'packages': [{
                'id': package.id,
                'quantity': package.quantity,
                'price': package.price
            }],

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
            'packages': [{
                'quantity': 16,
                'price': 100000,
            }]
        }

        calendar_counter = Calendar.objects.count()
        package_counter = CalendarPackage.objects.count()

        serializer = CalendarSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertEqual(Calendar.objects.count(), calendar_counter + 1)
        self.assertEqual(CalendarPackage.objects.count(), package_counter + 1)

    def test_update(self):
        """
        The serializer should update the data even the packages data
        """
        package = CalendarPackageFactory(calendar=self.calendar, price=100000, quantity=4)

        data = {
            'session_price': 500000,
            'packages': [{
                'id': package.id,
                'quantity': 6,
            }]
        }

        serializer = CalendarSerializer(self.calendar, data=data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()
        calendar = Calendar.objects.get(id=self.calendar.id)
        package = CalendarPackage.objects.get(id=package.id)
        self.assertEqual(calendar.session_price, 500000)
        self.assertEqual(package.quantity, 6)

    def test_create_other_package_in_update(self):
        """
        If the serializer receive one more package in the update method
        the package should be created
        """
        calendar = CalendarFactory(activity__is_open=True)
        packages = CalendarPackageFactory.create_batch(2, calendar=calendar)

        data = {
            'packages':[{
                'id': p.id,
                'quantity': p.quantity,
                'price': p.price,
            } for p in packages]
        }

        # The new package
        data['packages'].append({
            'quantity': 16,
            'price': 183740,
        })

        packages_counter = CalendarPackage.objects.count()

        serializer = CalendarSerializer(calendar, data=data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        serializer.save()
        self.assertEqual(CalendarPackage.objects.count(), packages_counter + 1)

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

    def test_if_activity_is_closed_session_price_should_be_required(self):
        """
        If the activity is_open is False the CalendarSerializer should require
        the session price and not the packages
        """
        today = now()
        epoch = UnixEpochDateField()
        activity = ActivityFactory(is_open=False)
        data = {
            'activity': activity.id,
            'initial_date': epoch.to_representation(today),
            'available_capacity': 10,
            'note': 'Note',
            'schedules': '<p><strong>Lunes - Viernes</strong></p><p>6:00pm - 9:00pm</p>',
        }

        serializer = CalendarSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, "{'session_price': ['Este campo es"
                                                       " requerido.']}"):
            serializer.is_valid(raise_exception=True)

    def test_if_activity_is_open_packages_should_be_required(self):
        """
        If the activity is_open is False the CalendarSerializer should require
        the session price and not the packages
        """
        today = now()
        epoch = UnixEpochDateField()
        activity = ActivityFactory(is_open=True)
        data = {
            'activity': activity.id,
            'initial_date': epoch.to_representation(today),
            'available_capacity': 10,
            'note': 'Note',
            'schedules': '<p><strong>Lunes - Viernes</strong></p><p>6:00pm - 9:00pm</p>',
        }

        serializer = CalendarSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, "{'packages': ['Este campo es"
                                                       " requerido.']}"):
            serializer.is_valid(raise_exception=True)

    def test_only_one_calendar_activity_open(self):
        """
        If the activity is open the serializer shouldn't let create more than 1 calendar
        """
        today = now()
        epoch = UnixEpochDateField()
        activity = ActivityFactory(is_open=True)
        CalendarFactory(activity=activity)
        data = {
            'activity': activity.id,
            'initial_date': epoch.to_representation(today),
            'available_capacity': 10,
            'note': 'Note',
            'schedules': '<p><strong>Lunes - Viernes</strong></p><p>6:00pm - 9:00pm</p>',
            'packages': [{
                'quantity': 3,
                'price': 123843,
            }]
        }

        serializer = CalendarSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, "{'non_field_errors': ['No se puede crear"
                                                       " más de un calendario cuando la actividad"
                                                       " es de horario abierto']}"):
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


class CalendarPackageSerializerTest(APITestCase):

    def test_read(self):
        data = {
            'quantity': 4,
            'price': 100000,
        }

        calendar_package = CalendarPackageFactory(**data)

        serializer = CalendarPackageSerializer(calendar_package)
        self.assertTrue(all(item in serializer.data.items() for item in data.items()))

    def test_update(self):
        package = CalendarPackageFactory(price=1000000)

        data = { 'price': 500000 }

        serializer = CalendarPackageSerializer(package, data=data, partial=True)
        self.assertTrue(serializer.is_valid(raise_exception=True))

        serializer.save()
        package = CalendarPackage.objects.get(id=package.id)

        self.assertEqual(package.price, 500000)

    def test_quantity_validation(self):
        package = CalendarPackageFactory()
        data = { 'quantity': 0 }

        serializer = CalendarPackageSerializer(package, data=data, partial=True)
        with self.assertRaisesMessage(ValidationError, "{'quantity': ['La cantidad no puede ser "
                                                       "menor a 1.']}"):
            serializer.is_valid(raise_exception=True)

    def test_price_validation(self):
        package = CalendarPackageFactory()
        data = { 'price': 10000 }

        serializer = CalendarPackageSerializer(package, data=data, partial=True)
        with self.assertRaisesMessage(ValidationError, "{'price': ['El precio no puede ser menor "
                                                       "a 30000.']}"):
            serializer.is_valid(raise_exception=True)
