from django.conf.urls import patterns, include, url
from .views import PhotoUploadView


urlpatterns = patterns('',

    url(r'^upload/photo/$', PhotoUploadView.as_view()),

	)