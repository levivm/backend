from django.conf.urls import url

from .views import PayUNotificationPayment, PayUBankList

urlpatterns = [
    url(r'^notification/?$', PayUNotificationPayment.as_view(), name='notification'),
    url(r'^pse/banks/?$', PayUBankList.as_view()),

]
