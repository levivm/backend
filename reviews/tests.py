import json
from rest_framework import status
from activities.models import Activity
from reviews.models import Review
from reviews.views import ReviewsViewSet, ReviewListByOrganizerViewSet, ReviewListByStudentViewSet
from utils.tests import BaseViewTest


class CreateReviewViewTest(BaseViewTest):
    ACTIVITY_ID = 1
    view = ReviewsViewSet

    def __init__(self, methodName='runTest'):
        super(CreateReviewViewTest, self).__init__(methodName)
        self.url = '/api/activities/%s/reviews' % self.ACTIVITY_ID

    def get_test_data(self):
        return {
            'rating': 4,
            'comment': 'De pana!',
        }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_student_should_create_a_review(self):
        reviews_count = Review.objects.count()
        activity = Activity.objects.get(id=self.ACTIVITY_ID)
        activity_reviews = activity.reviews.count()
        student = self.get_student_client()
        data = self.get_test_data()
        response = student.post(self.url, data=json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), reviews_count + 1)
        self.assertEqual(activity.reviews.count(), activity_reviews + 1)

    def test_another_student_shouldnt_create_a_review(self):
        reviews_count = Review.objects.count()
        student = self.get_student_client(user_id=self.ANOTHER_STUDENT_ID)
        data = self.get_test_data()
        response = student.post(self.url, data=json.dumps(data), **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), reviews_count)


class ReplyReviewViewTest(BaseViewTest):
    REVIEW_ID = 1
    view = ReviewsViewSet

    def __init__(self, methodName='runTest'):
        super(ReplyReviewViewTest, self).__init__(methodName)
        self.url = '/api/reviews/%s' % self.REVIEW_ID

    def get_test_data(self):
        return {
            'reply': 'Gracias',
            'rating': 2,
        }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_reply_a_review(self):
        organizer = self.get_organizer_client()
        data = self.get_test_data()
        response = organizer.put(self.url, data=json.dumps(data), **self.headers)
        review = Review.objects.get(id=self.REVIEW_ID)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(review.reply, 'Gracias')
        self.assertEqual(review.rating, 4)

    def test_another_organizer_shouldnt_reply_a_review(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        data = self.get_test_data()
        response = organizer.put(self.url, data=json.dumps(data), **self.headers)
        review = Review.objects.get(id=self.REVIEW_ID)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(review.reply, '')


class ReviewListByOrganizerViewTest(BaseViewTest):
    url = '/api/organizers/1/reviews/'
    view = ReviewListByOrganizerViewSet
    data = {'page': 1, 'page_size': 10}

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student, data=self.data)
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer, data=self.data)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


class ReviewListByStudentViewTest(BaseViewTest):
    url = '/api/students/1/reviews'
    view = ReviewListByStudentViewSet
    data = {'page': 1, 'page_size': 10}

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_anonymous_methods(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_organizer_methods(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_student_methods(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_another_student_shouldnt_get_the_reviews(self):
        student = self.get_student_client(user_id=self.ANOTHER_STUDENT_ID)
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)