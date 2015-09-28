from django.conf.urls import patterns, url
from reviews.views import ReportReviewView
from .views import ReviewsViewSet, ReviewListByOrganizerViewSet, ReviewListByStudentViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/reviews/?$', ReviewsViewSet.as_view({'post': 'create'}), name='review_rest_api'),
    url(r'^reviews/(?P<pk>\d+)/?$', ReviewsViewSet.as_view({'put': 'reply'}), name='review_rest_api'),
    url(r'^organizers/(?P<organizer_pk>\d+)/reviews/?$', ReviewListByOrganizerViewSet.as_view({'get': 'list'}), name='review_rest_api'),
    url(r'^students/(?P<student_pk>\d+)/reviews/?$', ReviewListByStudentViewSet.as_view({'get': 'list'}), name='review_rest_api'),
    url(r'^reviews/(?P<pk>\d+)/report/?$', ReportReviewView.as_view({'post': 'report'}), name="report_review_api"),
)