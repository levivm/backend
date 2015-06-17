from django.conf.urls import patterns, url
from students.views import StudentViewSet, StudentActivitiesViewSet

urlpatterns = patterns('',
   url(r'^(?P<pk>\d+)/?$', StudentViewSet.as_view({'put': 'update', 'get':'retrieve'})),
   url(r'^(?P<pk>\d+)/activities/?$', StudentActivitiesViewSet.as_view({'get':'retrieve'})),
)