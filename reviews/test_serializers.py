from mock import Mock
from django.utils.timezone import timedelta, now
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase
from activities.models import Activity, Calendar
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from students.models import Student


class ReviewSerializerTest(APITestCase):
    """
    Class to test the serializer ReviewSerializer
    """

    def setUp(self):
        self.activity = mommy.make(Activity)
        self.calendar = mommy.make(Calendar, activity=self.activity, initial_date=now() - timedelta(days=3))
        self.author = mommy.make(Student)
        self.data = {
            'rating': 5,
            'activity': self.activity.id,
        }
        self.context = self.get_context()

    def get_context(self):
        request = Mock()
        request.data = {'author': self.author}
        return {
            'request': request,
            'calendar': self.calendar,
        }

    def test_create(self):
        """
        Test create a review with the serializer
        """

        serializer = ReviewSerializer(data=self.data)
        serializer.context = self.context
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(Review.objects.filter(**self.data).exists())

        # Check the permissions
        perms = ('reviews.report_review', 'reviews.reply_review', 'reviews.read_review')
        self.activity.organizer.user.has_perms(perms)

    def test_read(self):
        """
        Test the serialization of an instance
        """

        review = Review.objects.create(rating=5, activity=self.activity, author=self.author)
        serializer = ReviewSerializer(review)

        content = {**self.data, **{'created_at': review.created_at.isoformat()[:-6] + 'Z'}}
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    def test_reply(self):
        """
        Test the reply
        """

        # Arrangement
        review = Review.objects.create(rating=5, activity=self.activity, author=self.author)
        data = {'reply': 'Replied'}

        serializer = ReviewSerializer(review, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        review = Review.objects.get(id=review.id)
        self.assertEqual(review.reply, 'Replied')

    def test_validate_rating(self):
        """
        Test to validate that rating should be in range of 0-5
        """

        self.data['rating'] = 6

        with self.assertRaises(ValidationError):
            serializer = ReviewSerializer(data=self.data)
            serializer.is_valid(raise_exception=True)

    def test_validate_reply(self):
        """
        Test can't change reply
        """

        # Arrangement
        review = Review.objects.create(rating=5, activity=self.activity, author=self.author, reply='Replied')
        data = {'reply': 'Replied updated'}

        with self.assertRaisesMessage(ValidationError, "{'reply': ['No se puede cambiar la respuesta']}"):
            serializer = ReviewSerializer(review, data=data, partial=True)
            serializer.is_valid(raise_exception=True)

    def test_validate_calendar_passed(self):
        """
        Test can't create if there is not calendar
        """

        del self.context['calendar']

        with self.assertRaisesMessage(ValidationError, "{'non_field_errors': ['Se necesita el calendario']}"):
            serializer = ReviewSerializer(data=self.data)
            serializer.context = self.context
            serializer.is_valid(raise_exception=True)

    def test_validate_calendar_activity(self):
        """
        The calendar's activity should be the same as the GET's activity
        """

        self.context['calendar'] = mommy.make(Calendar)

        with self.assertRaisesMessage(ValidationError,
                                      "{'non_field_errors': ['El calendario no es de esa actividad']}"):
            serializer = ReviewSerializer(data=self.data)
            serializer.context = self.context
            serializer.is_valid(raise_exception=True)

    def test_validate_calendar_initial_date(self):
        """
        Now() should be grater than calendar.initial_date
        """

        # Set the initial_date 10 days ahead
        self.calendar.initial_date = now() + timedelta(days=10)
        self.calendar.save()

        with self.assertRaisesMessage(ValidationError,
                                      "{'non_field_errors': ['No se puede crear antes de que empiece la actividad']}"):
            serializer = ReviewSerializer(data=self.data)
            serializer.context = self.context
            serializer.is_valid(raise_exception=True)
