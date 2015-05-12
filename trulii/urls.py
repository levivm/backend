from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.urlpatterns import format_suffix_patterns
from organizers.api import OrganizerDetail,InstructorDetail
from django.conf import settings
#from users.views import SignUpAjax
from users.views import ChangeEmailView,PasswordChange

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

#if settings.DEBUG :

urlpatterns = patterns('',
    # Examples:
    
    url(r'^home$', 'landing.views.landing', name='home'),
    url(r'^form_modal$', 'landing.views.form_modal', name='form_modal'),

    # url(r'^blog/', include('blog.urls')),

	# (r'^users/logout/$', 'django.contrib.auth.views.logout',
 #     	{'next_page': '/'}),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/email/', ChangeEmailView.as_view()),
    url(r'^users/password/change/', PasswordChange.as_view()),
    #url(r'^password/reset/', ResetPassword.as_view()),
    url(r'^users/', include('allauth.urls')),
    url(r'^api/users/', include('users.urls')),
    url(r'^api/organizers/', include('organizers.urls')),
    url(r'^api/activities', include('activities.urls')),
 	url(r'^api/locations/', include('locations.urls')),
 	url(r'^api/students/', include('students.urls')),
    url(r'^api/', include('orders.urls')),
    url(r'^docs/', include('rest_framework_swagger.urls')),

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


#
if  not settings.DEBUG:
    #urlpatterns += staticfiles_urlpatterns()
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )

#

urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)

