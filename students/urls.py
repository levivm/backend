from django.conf.urls import patterns, url
from .views import StudentViewSet

urlpatterns = patterns('',
   url(r'^(?P<pk>\d+)/?$', StudentViewSet.as_view({'put': 'partial_update','get':'retrieve'})),
)