import datetime
from mock import Mock, patch
from django.utils.timezone import timedelta, now, utc
from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.factories import ActivityFactory
from activities.models import Activity, Calendar
from orders.factories import OrderFactory
from orders.models import Order
from reviews.factories import ReviewFactory
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from students.models import Student


class ReviewSerializerTest(APITestCase):
    """
    Class to test the serializer ReviewSerializer
    """

    def setUp(self):
        self.activity = ActivityFactory()
        self.author = mommy.make(Student)
        self.order = OrderFactory(status=Order.ORDER_APPROVED_STATUS, calendar__activity=self.activity,
                                calendar__initial_date=now() - timedelta(days=3), student=self.author)
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

        content = {
            **self.data,
            'created_at': review.created_at.isoformat()[:-6] + 'Z',
            'activity_data':{
                'id': self.activity.id,
                'title': self.activity.title,
            }
        }
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    def test_reply(self):
        """
        Test the reply
        """

        # Arrangement
        review = Review.objects.create(rating=5, activity=self.activity, author=self.author)
        data = {'reply': 'Replied'}
        replied_at = datetime.datetime(2015, 11, 8, 3, 30, 0, tzinfo=utc)

        with patch('reviews.serializers.now') as mock_now:
            mock_now.return_value = replied_at
            serializer = ReviewSerializer(review, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

        review = Review.objects.get(id=review.id)
        self.assertEqual(review.reply, 'Replied')
        self.assertEqual(review.replied_at, replied_at)
        self.assertEqual(serializer.data['replied_at'], replied_at.isoformat()[:-6] + 'Z')

    def test_validate_rating(self):
        """
        Test to validate that rating should be in range of 1-5
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

    def test_validate_calendar_initial_date(self):
        """
        Now() should be grater than calendar.initial_date
        """

        # Set the initial_date 10 days ahead
        self.order.calendar.initial_date = now() + timedelta(days=10)
        self.order.calendar.save()

        with self.assertRaisesMessage(ValidationError,
                                      "{'non_field_errors': ['La orden no cumple con los "
                                      "requerimientos para crear un review']}"):
            serializer = ReviewSerializer(data=self.data)
            serializer.context = self.context
            serializer.is_valid(raise_exception=True)

    def test_change_replied_at(self):
        """
        Shouldn't be able to change the replied_at date if is set
        """

        replied_at = datetime.datetime(2015, 11, 8, 3, 30, 0, tzinfo=utc)
        review = ReviewFactory(reply='Replied', replied_at=replied_at)

        serializer = ReviewSerializer(review, data={'rating': 2}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        review = Review.objects.get(id=review.id)
        self.assertEqual(review.replied_at, replied_at)

    def test_without_rating(self):
        """
        Test trying to create a review without rating
        """

        del self.data['rating']

        with self.assertRaises(ValidationError):
            serializer = ReviewSerializer(data=self.data)
            serializer.is_valid(raise_exception=True)
