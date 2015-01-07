from django.conf.urls import patterns, include, url
from .views import signup,PhotoUploadView


urlpatterns = patterns('',

    url(r'^signup/$', signup),
    url(r'^api/organizer/upload/photo$', PhotoUploadView.as_view()),

	)