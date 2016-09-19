from django.conf import settings
from django.conf.urls import include, url
from django.contrib.gis import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.urlpatterns import format_suffix_patterns

from landing.views import ContactFormView, landing, form_modal

urlpatterns = [

    url(r'^home$', landing, name='home'),
    url(r'^form_modal$', form_modal, name='form_modal'),
    url('^admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    url(r'^olympus/', include(admin.site.urls)),
    url(r'^api/contact-us/', ContactFormView.as_view(), name='contact_form'),
    url(r'^api/auth/', include('authentication.urls', namespace='auth')),
    url(r'^api/users/', include('users.urls', namespace='users')),
    url(r'^api/', include('organizers.urls', namespace='organizers')),
    url(r'^api/activities/', include('activities.urls', namespace='activities')),
    url(r'^api/locations/', include('locations.urls')),
    url(r'^api/students/', include('students.urls', namespace='students')),
    url(r'^api/payments/', include('payments.urls', namespace='payments')),
    url(r'^api/', include('orders.urls', namespace='orders')),
    url(r'^api/', include('reviews.urls', namespace='reviews')),
    url(r'^api/referrals/', include('referrals.urls', namespace='referrals')),
    url(r'^api/messages/', include('messages.urls', namespace='messages')),
    url(r'^api/balances/', include('balances.urls', namespace='balances')),
    url(r'^metrics/', include('metrics.urls', namespace='metrics')),
    url(r'^docs/', include('rest_framework_swagger.urls')),

]

#
if not settings.DEBUG:
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
        url(r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_ROOT}),
    ]

urlpatterns += staticfiles_urlpatterns()

urlpatterns = format_suffix_patterns(urlpatterns)
