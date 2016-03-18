from django.conf import settings
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.models import Calendar, Activity
from activities.serializers import CalendarSerializer, CategoriesSerializer, ActivityPhotosSerializer, \
    ActivitiesSerializer
from locations.serializers import LocationsSerializer
from orders.models import Assistant, Order
from orders.serializers import AssistantsSerializer
from organizers.serializers import OrganizersSerializer
from utils.serializers import UnixEpochDateField


class CalendarSerializerTest(APITestCase):
    """
    Test cases for CalendarSerializer
    """

    def setUp(self):
        self.calendar = mommy.make(Calendar, session_price=100000)
        self.order = mommy.make(Order, status=Order.ORDER_APPROVED_STATUS, calendar=self.calendar, quantity=3)
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
            'closing_sale': epoch.to_representation(self.calendar.closing_sale),
            'number_of_sessions': self.calendar.number_of_sessions,
            'session_price': self.calendar.session_price,
            'capacity': self.calendar.capacity,
            'sessions': [],
            'assistants': AssistantsSerializer(self.calendar.get_assistants(), many=True,
                                               remove_fields=['student']).data,
            'is_weekend': self.calendar.is_weekend,
            'duration': self.calendar.duration,
            'is_free': self.calendar.is_free,
            'available_capacity': self.calendar.available_capacity(),

        }
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))


class ActivitySerializerTest(APITestCase):
    """
    Test for ActivitySerializer
    """

    def setUp(self):
        self.activity = mommy.make(Activity)

    def test_read(self):
        """
        Test the serializer data
        """

        category_data = CategoriesSerializer(instance=self.activity.sub_category.category,
                                             remove_fields=['subcategories']).data
        # location_data = LocationsSerializer(self.activity.location).data
        last_date = UnixEpochDateField().to_representation(self.activity.last_sale_date())
        organizer_data = OrganizersSerializer(self.activity.organizer).data

        content = {
            'id': self.activity.id,
            'title': self.activity.title,
            'short_description': self.activity.short_description,
            'sub_category': self.activity.sub_category.id,
            'sub_category_display': self.activity.sub_category.name,
            'level': self.activity.level,
            'level_display': self.activity.get_level_display(),
            # 'tags',
            'category': category_data,
            'content': self.activity.content,
            'requirements': self.activity.requirements,
            'return_policy': self.activity.return_policy,
            'extra_info': self.activity.extra_info,
            'audience': self.activity.audience,
            'goals': self.activity.goals,
            'methodology': self.activity.methodology,
            # 'location': location_data,
            # 'pictures': ,
            'youtube_video_url': self.activity.youtube_video_url,
            'published': self.activity.published,
            'certification': self.activity.certification,
            'last_date': last_date,
            'calendars': [],
            # 'closest_calendar',
            # 'required_steps': ,
            'steps': settings.ACTIVITY_STEPS,
            'organizer': organizer_data,
            'instructors': [],
            'score': self.activity.score,
            'rating': self.activity.rating,
        }

        serializer = ActivitiesSerializer(self.activity)
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))
