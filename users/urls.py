from django.conf.urls import patterns, include, url
from .views import PhotoUploadView,UsersView


urlpatterns = patterns('',

    url(r'^upload/photo/$', PhotoUploadView.as_view()),
    url(r'^current/$', UsersView.as_view()),

	)