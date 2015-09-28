from django.conf.urls import patterns, include, url
from organizers.views import InstructorViewSet, ActivityInstructorViewSet
from .views import signup,OrganizerViewSet,OrganizerInstructorViewSet,OrganizerLocationViewSet

from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(, OrganizerViewSet)
# urlpatterns = router.urls



urlpatterns = patterns('',

    url(r'^organizers/signup/$', signup),
    url(r'^organizers/(?P<organizer_pk>\d+)/?$', OrganizerViewSet.as_view({'put': 'partial_update','get':'retrieve'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/activities/?$', OrganizerViewSet.as_view({'get':'activities'})),
    # url(r'^(?P<pk>\d+)/locations/?$', OrganizerViewSet.as_view({'post':'set_location'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/locations/?$', OrganizerLocationViewSet.as_view({'post':'set_location'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/instructors/?$', OrganizerInstructorViewSet.as_view({'get':'list', 'post': 'create'})),
    url(r'^instructors/(?P<pk>\d+)/?$', InstructorViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    url(r'^activities/(?P<activity_pk>\d+)/instructors/?$', ActivityInstructorViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^activities/(?P<activity_pk>\d+)/instructors/(?P<pk>\d+)?$', ActivityInstructorViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
)


