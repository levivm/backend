from django.conf.urls import patterns, include, url
from .views import signup,OrganizerViewSet

from rest_framework.routers import DefaultRouter




urlpatterns = patterns('',

    url(r'^signup/$', signup),
    url(r'^(?P<pk>\d+)/$', OrganizerViewSet.as_view({'post': 'partial_update'})),
	)


