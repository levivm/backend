from django.conf.urls import patterns, include, url
from .views import signup,OrganizerViewSet

from rest_framework.routers import DefaultRouter


# router = DefaultRouter()
# router.register(, OrganizerViewSet)
# urlpatterns = router.urls



urlpatterns = patterns('',

    url(r'^signup/$', signup),
    url(r'^(?P<pk>\d+)/?$', OrganizerViewSet.as_view({'put': 'partial_update','get':'retrieve'})),
	)


