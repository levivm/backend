from django.conf.urls import patterns, include, url
from .views import PhotoUploadView,UsersViewSet,ObtainAuthTokenView, RequestSignupViewSet


urlpatterns = patterns('',

	url(r'^token/', ObtainAuthTokenView.as_view()),
    url(r'^upload/photo/?$', PhotoUploadView.as_view()),
    url(r'^current/?$', UsersViewSet.as_view({'get':'retrieve'})),
    url(r'^logout/?$', UsersViewSet.as_view({'post':'logout'})),
    url(r'^request/signup/?$', RequestSignupViewSet.as_view({'post':'create'})),
    


	)