from django.conf.urls import *
#from activities import views
from views import CitiesViewSet



urlpatterns = patterns('',
	#url(r'^categories/?$',ListCategories.as_view()),

	url(r'^cities/?$',CitiesViewSet.as_view({'get':'list'})),
	url(r'^city/?$',CitiesViewSet.as_view({'post':'create'})),

	)