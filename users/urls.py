from django.conf.urls import url

from .views import PhotoUploadView,UsersViewSet, RequestSignupViewSet

urlpatterns = [
    url(r'^upload/photo/?$', PhotoUploadView.as_view()),
    url(r'^current/?$', UsersViewSet.as_view({'get':'retrieve'})),
	url(r'^request/signup/token/(?P<key>\w+)/$', UsersViewSet.as_view({'get':'verify_organizer_pre_signup_key'})),
    url(r'^request/signup/?$', RequestSignupViewSet.as_view({'post':'create'}), name='request_signup'),
]
