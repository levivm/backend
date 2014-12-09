from django.conf.urls import patterns, include, url
from .views import signup


urlpatterns = patterns('',

    url(r'^signup/$', signup),

	)