from mock import Mock

from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from activities.models import Activity
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from students.models import Student


class ReviewSerializerTest(APITestCase):
    """
    Class to test the serializer ReviewSerializer
    """

    def setUp(self):
        self.activity = mommy.make(Activity)
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
            'request': request
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

    def test_read(self):
        """
        Test the serialization of an instance
        """

        review = Review.objects.create(rating=5, activity=self.activity, author=self.author)
        serializer = ReviewSerializer(review)

        content = {**self.data, **{'created_at': review.created_at.isoformat()[:-6] + 'Z'}}
        self.assertTrue(all(item in serializer.data.items() for item in content.items()))

    def test_validate_rating(self):
        """
        Test to validate that rating should be in range of 0-5
        """

        self.data['rating'] = 6

        with self.assertRaises(ValidationError):
            serializer = ReviewSerializer(data=self.data)
            serializer.is_valid(raise_exception=True)
