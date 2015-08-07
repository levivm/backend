from django.conf.urls import patterns, url
from .views import PayUNotificationPayment


urlpatterns = patterns('',
   url(r'^notification/?$', PayUNotificationPayment.as_view()),
)