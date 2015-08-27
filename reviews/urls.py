from django.conf.urls import patterns, url
from .views import ReviewsViewSet, ReviewListByOrganizerViewSet, ReviewListByStudentViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/reviews/?$', ReviewsViewSet.as_view({'post': 'create'})),
    url(r'^reviews/(?P<pk>\d+)/?$', ReviewsViewSet.as_view({'put': 'reply'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/reviews/?$', ReviewListByOrganizerViewSet.as_view({'get': 'list'})),
    url(r'^students/(?P<student_pk>\d+)/reviews/?$', ReviewListByStudentViewSet.as_view({'get': 'list'})),
)