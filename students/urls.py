from django.conf.urls import patterns, url
from students.views import StudentViewSet, StudentActivitiesViewSet

urlpatterns = [
    url(r'^(?P<pk>\d+)/?$', StudentViewSet.as_view({'put': 'partial_update', 'get':'retrieve'})),
    url(r'^(?P<pk>\d+)/activities/?$', StudentActivitiesViewSet.as_view({'get':'retrieve'}), name="activities"),
    url(r'^(?P<pk>\d+)/activities/autocomplete/?$', StudentActivitiesViewSet.as_view({'get':'autocomplete'}), 
    										        name="activities_autocomplete"),
]
