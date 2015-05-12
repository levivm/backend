from django.conf.urls import patterns, include, url
from .views import signup,OrganizerViewSet,InstructorViewSet

from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(, OrganizerViewSet)
# urlpatterns = router.urls



urlpatterns = patterns('',

    url(r'^signup/$', signup),
    url(r'^(?P<pk>\d+)/?$', OrganizerViewSet.as_view({'put': 'partial_update','get':'retrieve'})),
    url(r'^(?P<pk>\d+)/activities/?$', OrganizerViewSet.as_view({'get':'activities'})),
    url(r'^(?P<pk>\d+)/locations/?$', OrganizerViewSet.as_view({'post':'set_location'})),
    url(r'^(?P<organizer_id>\d+)/instructors/(?P<instructor_id>\d+)/?$', InstructorViewSet.as_view({'delete':'destroy'})),
	)


