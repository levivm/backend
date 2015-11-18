import json
from datetime import datetime

import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.utils.timezone import now, timedelta, utc
from guardian.shortcuts import assign_perm
from model_mommy import mommy
from rest_framework import status
from rest_framework.reverse import reverse

from activities.models import Activity, Calendar
from orders.models import Order
from reviews.models import Review
from utils.tests import BaseAPITestCase


class ReviewAPITest(BaseAPITestCase):
    """
    Class to test the Review API functionality
    """
    headers = {'content_type': 'application/json'}

    def setUp(self):
        # Calling the super (initialization)
        super(ReviewAPITest, self).setUp()

        # Objects needed
        self.activity = mommy.make(Activity, organizer=self.organizer, published=True)
        self.calendar = mommy.make(Calendar, activity=self.activity, initial_date=now() - timedelta(days=2))
        self.order = mommy.make(Order, student=self.student, calendar=self.calendar, status=Order.ORDER_APPROVED_STATUS)
        self.post = {'rating': 4, 'comment': 'First comment!'}
        self.put = {'rating': 2, 'reply': 'Thank you!'}
        self.review = mommy.make(Review, author=self.student, activity=self.activity, **self.post)

        # URLs
        self.list_by_organizer_url = reverse('reviews:list_by_organizer', kwargs={'organizer_pk': self.organizer.id})
        self.list_by_student_url = reverse('reviews:list_by_student', kwargs={'student_pk': self.student.id})
        self.create_url = reverse('reviews:create', kwargs={'activity_pk': self.activity.id})
        self.retrieve_update_delete_url = reverse('reviews:reply', kwargs={'pk': self.review.id})
        self.report_url = reverse('reviews:report', kwargs={'pk': self.review.id})
        self.read_url = reverse('reviews:read', kwargs={'pk': self.review.id})

        # Counters
        self.review_count = Review.objects.count()
        self.activity_reviews = self.activity.reviews.count()

        # Set permissions
        add_review = Permission.objects.get_by_natural_key('add_review', 'reviews', 'review')
        add_review.user_set.add(self.student.user, self.another_student.user)
        change_review = Permission.objects.get_by_natural_key('change_review', 'reviews', 'review')
        change_review.user_set.add(self.organizer.user, self.another_organizer.user)
        assign_perm('reviews.reply_review', user_or_group=self.organizer.user, obj=self.review)
        assign_perm('reviews.report_review', user_or_group=self.organizer.user, obj=self.review)
        assign_perm('reviews.read_review', user_or_group=self.organizer.user, obj=self.review)

    def test_list_by_organizer(self):
        """
        Test to list the reviews by organizer
        """

        # Anonymous should return a list of reviews
        response = self.client.get(self.list_by_organizer_url)
        self.assertContains(response, self.post.get('comment'))

        # Student should return a list of reviews
        response = self.student_client.get(self.list_by_organizer_url)
        self.assertContains(response, self.post.get('comment'))

        # Organizer should return a list of reviews
        response = self.organizer_client.get(self.list_by_organizer_url)
        self.assertContains(response, self.post.get('comment'))

    def test_list_by_student(self):
        """
        Test to list the reviews of a student
        """

        # Anonymous should return unathorized
        response = self.client.get(self.list_by_student_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should not get the reviews
        response = self.organizer_client.get(self.list_by_student_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student who is not the owner should not get the reviews
        response = self.another_student_client.get(self.list_by_student_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Student owner should get the reviews
        response = self.student_client.get(self.list_by_student_url)
        self.assertContains(response, self.post.get('comment'))

    def test_create(self):
        """
        Test to create a review [POST]
        """

        # Anonymous should return unauthorized
        response = self.client.post(self.create_url, self.post)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), self.review_count)

        # Organizer should return forbidden
        response = self.organizer_client.post(self.create_url, self.post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), self.review_count)

        # Student without order should not create a review
        response = self.another_student_client.post(self.create_url, self.post)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), self.review_count)

        # Student should create a review
        response = self.student_client.post(self.create_url, self.post)
        review = Review.objects.get(id=response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertEqual(Review.objects.count(), self.review_count + 1)
        self.assertEqual(self.activity.reviews.count(), self.activity_reviews + 1)
        self.assertTrue(self.activity.organizer.user.has_perm(perm='reviews.reply_review', obj=review))
        self.assertTrue(self.activity.organizer.user.has_perm(perm='reviews.report_review', obj=review))

    def test_retrieve(self):
        """
        Test to retrieve a review [GET]
        """

        # Anonymous should return unauthorized
        response = self.client.get(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should not retrive a review
        response = self.organizer_client.get(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # Student should not retrive a review
        response = self.student_client.get(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update(self):
        """
        Test to reply a review [PUT]
        """

        # Anonymous should return unauthorized
        response = self.client.put(self.retrieve_update_delete_url, self.put)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should not reply a review
        response = self.student_client.put(self.retrieve_update_delete_url, self.put)
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(review.reply, '')

        # Organizer should not reply a review if he is not the owner of the activity
        response = self.another_organizer_client.put(self.retrieve_update_delete_url, self.put)
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(review.reply, '')

        # Organizer should reply a review
        replied_at = datetime(2015, 11, 8, 3, 30, tzinfo=utc)
        with mock.patch('reviews.serializers.now') as mock_now:
            mock_now.return_value = replied_at
            response = self.organizer_client.put(self.retrieve_update_delete_url, self.put)

        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(review.reply, 'Thank you!')
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.replied_at, replied_at)

    def test_delete(self):
        """
        Test to delete a review [DELETE]
        """

        # Anoymous should return unauthorized
        response = self.client.delete(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Review.objects.count(), self.review_count)

        # Student should not delete a review
        response = self.student_client.delete(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), self.review_count)

        # Organizer should not delete a review
        response = self.organizer_client.delete(self.retrieve_update_delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Review.objects.count(), self.review_count)

    def test_report(self):
        """
        Test report a review [POST]
        """
        # Set Celery
        settings.CELERY_ALWAYS_EAGER = True

        # Anonymous should return unauthorized
        response = self.client.post(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should not report a review
        response = self.student_client.post(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer who is not the owner should not report a review
        response = self.another_organizer_client.post(self.report_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer owner should report a review
        response = self.organizer_client.post(self.report_url)
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(review.reported)

    def test_mark_as_read(self):
        """
        Test a review marked as read
        """

        data = json.dumps({'read': True})

        # Anonymous should return unauthorized
        response = self.client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should mark the review as read
        response = self.organizer_client.put(self.read_url, data=data, **self.headers)
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(review.read)

        # Organizer who is not the owner should not read a review
        response = self.another_organizer_client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_mark_as_unread(self):
        """
        Test a review marked as unread
        """

        self.review.read = True
        self.review.save()
        data = json.dumps({'read': False})

        # Anonymous should return unauthorized
        response = self.client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should return forbidden
        response = self.student_client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should mark the review as read
        response = self.organizer_client.put(self.read_url, data=data, **self.headers)
        review = Review.objects.get(id=self.review.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(review.read)

        # Organizer who is not the owner should not read a review
        response = self.another_organizer_client.put(self.read_url, data=data, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)