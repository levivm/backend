from django.conf.urls import patterns, url
from .views import ReviewsViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/reviews/?$', ReviewsViewSet.as_view({'post': 'create'})),
    url(r'^reviews/(?P<pk>\d+)/?$', ReviewsViewSet.as_view({'put': 'reply'})),
)