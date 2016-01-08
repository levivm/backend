from django.conf.urls import url

from .views import PayUNotificationPayment,PayUBankList,PayUPSE

urlpatterns = [
    url(r'^notification/?$', PayUNotificationPayment.as_view(), name='notification'),
    url(r'^pse/banks/?$', PayUBankList.as_view()),
    url(r'^pse/response/?$', PayUPSE.as_view({'get':'payment_response'})),
    url(r'^pse/?$', PayUPSE.as_view({'post':'post'})),
    # url(r'^activity/?$', PayUPSE.as_view({'post':'post'})),

]
