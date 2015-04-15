from django.conf.urls import *
#from activities import views
from views import ActivitiesViewSet,ListCategories,CategoriesViewSet,\
				  SubCategoriesViewSet,TagsViewSet,ChronogramsViewSet
from rest_framework.routers import DefaultRouter
from rest_framework import routers



urlpatterns = patterns('',
	#url(r'^categories/?$',ListCategories.as_view()),
	url(r'^/?$',ActivitiesViewSet.as_view({'get':'list','post':'create'})),
	url(r'^(?P<pk>\d+)/?$',ActivitiesViewSet.as_view({'get':'retrieve','put': 'partial_update'})),
	url(r'^(?P<activity_pk>\d+)/calendars/?$',ChronogramsViewSet.as_view({'get':'list','post':'create'})),
	url(r'^(?P<activity_pk>\d+)/calendars/(?P<calendar_pk>\d+)/?$',ChronogramsViewSet.as_view({\
		                            'put': 'update','get':'retrieve','delete':'destroy'})),

	# url(r'^(?P<pk>\d+)/calendars/?$',ActivitiesViewSet.as_view({'post':'create_calendar',\
	# 	                            'put': 'update_calendar','get':'get_calendars','delete':'delete_calendar'})),
	
	url(r'^(?P<pk>\d+)/publish/?$',ActivitiesViewSet.as_view({'put':'publish'})),
	url(r'^(?P<pk>\d+)/gallery/?$',ActivitiesViewSet.as_view({'post':'add_photo','put':'delete_photo'})),

	url(r'^info/?$',ActivitiesViewSet.as_view({'get':'general_info'})),
	url(r'^tags/?$',TagsViewSet.as_view({'get':'list'})),
	url(r'^tag/?$',TagsViewSet.as_view({'post':'create'})),
	url(r'^ /?$',CategoriesViewSet.as_view({'get':'list'})),
	url(r'^category/?$',CategoriesViewSet.as_view({'post':'create'})),
	url(r'^subcategories/?$',SubCategoriesViewSet.as_view({'get':'list'})),
	url(r'^subcategory/?$',SubCategoriesViewSet.as_view({'post':'create'})),
	)