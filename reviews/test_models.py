from rest_framework.test import APITestCase

from reviews.factories import ReviewFactory


class ReviewTestCase(APITestCase):
    """
    Class for testing the Review model
    """

    def setUp(self):
        self.review = ReviewFactory()

    def test_permissions(self):
        user = self.review.activity.organizer.user

        self.assertTrue(user.has_perm('reviews.report_review', self.review))
        self.assertTrue(user.has_perm('reviews.reply_review', self.review))
        self.assertTrue(user.has_perm('reviews.read_review', self.review))
