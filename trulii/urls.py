from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework.urlpatterns import format_suffix_patterns

from users.views import ChangeEmailView,PasswordChange,ConfirmEmail,RestFacebookLogin
from landing.views import ContactFormView, landing, form_modal

from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [
    # Examples:
    
    url(r'^home$', landing, name='home'),
    url(r'^form_modal$', form_modal, name='form_modal'),

    # url(r'^blog/', include('blog.urls')),

	# (r'^users/logout/$', 'django.contrib.auth.views.logout',
 #     	{'next_page': '/'}),

    # url('^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^olympus/', include(admin.site.urls)),
    # url(r'^users/login/', LoginViewTest.as_view()),
    url(r'^api/contact-us/', ContactFormView.as_view(), name='contact_form'),
    url(r'^users/email/', ChangeEmailView.as_view()),
    url(r'^users/confirm-email/(?P<key>\w+)/', ConfirmEmail.as_view()),
    url(r'^users/facebook/signup/', RestFacebookLogin.as_view(), name='facebook_signup_login'),
    url(r'^users/password/change/', PasswordChange.as_view()),
    url(r'^users/', include('allauth.urls')),
    url(r'^api/users/', include('users.urls', namespace='users')),
    url(r'^api/', include('organizers.urls', namespace='organizers')),
    url(r'^api/activities/', include('activities.urls',namespace='activities')),
 	url(r'^api/locations/', include('locations.urls')),
    url(r'^api/students/', include('students.urls')),
 	url(r'^api/payments/', include('payments.urls', namespace='payments')),
    url(r'^api/', include('orders.urls',namespace='orders')),
 	url(r'^api/', include('reviews.urls',namespace='reviews')),
 	url(r'^api/referrals/', include('referrals.urls', namespace='referrals')),
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
    
    
    # url(r'^.*$', 'landing.views.landing', name='home'),

]


#
if  not settings.DEBUG:
    #urlpatterns += staticfiles_urlpatterns()
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    ]

#

urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)

