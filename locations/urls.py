from django.conf.urls import *
from .views import CitiesViewSet



urlpatterns = patterns('',
	#url(r'^categories/?$',ListCategories.as_view()),

	url(r'^cities/?$',CitiesViewSet.as_view({'get':'list'})),
	# url(r'^city/?$',CitiesViewSet.as_view({'post':'create'})),
	# url(r'^city/(?P<pk>\d+)/?$',CitiesViewSet.as_view({'get':'retrieve','post':'update'})),
	)