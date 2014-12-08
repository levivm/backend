from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from activities import api

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'trulii.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

	(r'^users/logout/$', 'django.contrib.auth.views.logout',
     	{'next_page': '/'}),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('allauth.urls')),

    #create the views for the detail activity and lists
    #API

    url(r'^api/activities/$', api.ActivityList.as_view()),
    url(r'^api/activities/(?P<pk>[0-9]+)/$', api.ActivityDetail.as_view()),

    ##create the view for the organizers
    url(r'^api/organizers/(?P<pk>[0-9]+)/$', api.OrganizerDetail.as_view()),

    ## create the view for the instructor
    url(r'^api/instructor/(?P<pk>[0-9]+)/$', api.InstructorDetail.as_view()),


)

	urlpatterns = format_suffix_patterns(urlpatterns)
