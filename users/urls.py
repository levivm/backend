from django.conf.urls import patterns, include, url
from .views import PhotoUploadView,UsersViewSet,ObtainAuthTokenView


urlpatterns = patterns('',

	url(r'^token/', ObtainAuthTokenView.as_view()),
    url(r'^upload/photo/?$', PhotoUploadView.as_view()),
    url(r'^current/?$', UsersViewSet.as_view({'get':'retrieve'})),

	)