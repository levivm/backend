from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns
from activities.api import ActivitiesList,ActivityDetail
from organizers.api import OrganizerDetail,InstructorDetail

urlpatterns = patterns('',
    # Examples:
    url(r'^home$', 'landing.views.landing', name='home'),
    url(r'^form_modal$', 'landing.views.form_modal', name='form_modal'),

    # url(r'^blog/', include('blog.urls')),

	# (r'^users/logout/$', 'django.contrib.auth.views.logout',
 #     	{'next_page': '/'}),

 #    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('allauth.urls')),
 #    url(r'^organizers/', include('organizers.urls')),
 #    #url(r'^organizers/', include('allauth.urls')),


 #    #create the views for the detail activity and lists
 #    #API

 #    url(r'^activities/$', ActivitiesList.as_view()),
 #    url(r'^activities/(?P<pk>[0-9]+)/$', ActivityDetail.as_view()),

 #    ##create the view for the organizers
 #    url(r'^organizers/(?P<pk>[0-9]+)/$', OrganizerDetail.as_view()),

 #    ## create the view for the instructor
 #    url(r'^instructor/(?P<pk>[0-9]+)/$', InstructorDetail.as_view()),

    url(r'^.*$', 'landing.views.landing', name='home'),


)

urlpatterns = format_suffix_patterns(urlpatterns)
