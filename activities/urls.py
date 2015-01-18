from django.conf.urls import *
#from activities import views
from views import ActivitiesViewSet,ListCategories,CategoriesViewSet,SubCategoriesViewSet,TagsViewSet
from rest_framework.routers import DefaultRouter
from rest_framework import routers



urlpatterns = patterns('',
	#url(r'^categories/?$',ListCategories.as_view()),
	url(r'^/?$',ActivitiesViewSet.as_view({'get':'list','post':'create'})),
	url(r'^(?P<pk>\d+)/?$',ActivitiesViewSet.as_view({'get':'retrieve','put': 'partial_update'})),
	url(r'^info/?$',ActivitiesViewSet.as_view({'get':'general_info'})),
	url(r'^tags/?$',TagsViewSet.as_view({'get':'list'})),
	url(r'^tag/?$',TagsViewSet.as_view({'post':'create'})),
	url(r'^categories/?$',CategoriesViewSet.as_view({'get':'list'})),
	url(r'^category/?$',CategoriesViewSet.as_view({'post':'create'})),
	url(r'^subcategories/?$',SubCategoriesViewSet.as_view({'get':'list'})),
	url(r'^subcategory/?$',SubCategoriesViewSet.as_view({'post':'create'})),
	)