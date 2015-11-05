from django.conf.urls import patterns, url
from reviews.views import ReportReviewView
from .views import ReviewsViewSet, ReviewListByOrganizerViewSet, ReviewListByStudentViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/reviews/?$', ReviewsViewSet.as_view({'post': 'create'}), name='create'),
    url(r'^reviews/(?P<pk>\d+)/read/?$', ReviewsViewSet.as_view({'put': 'read'}), name='read'),
    url(r'^reviews/(?P<pk>\d+)/?$', ReviewsViewSet.as_view({'put': 'reply'}), name='reply'),
    url(r'^organizers/(?P<organizer_pk>\d+)/reviews/?$', ReviewListByOrganizerViewSet.as_view({'get': 'list'}), name='list_by_organizer'),
    url(r'^students/(?P<student_pk>\d+)/reviews/?$', ReviewListByStudentViewSet.as_view({'get': 'list'}), name='list_by_student'),
    url(r'^reviews/(?P<pk>\d+)/report/?$', ReportReviewView.as_view({'post': 'report'}), name="report"),
)