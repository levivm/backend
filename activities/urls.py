from django.conf.urls import patterns, url
from .views import ActivitiesViewSet, CategoriesViewSet, \
    SubCategoriesViewSet, TagsViewSet, ChronogramsViewSet, \
    ActivityPhotosViewSet


urlpatterns = patterns('',  # url(r'^/categories/?$',ListCategories.as_view()),
    url(r'^/?$', ActivitiesViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/(?P<pk>\d+)/?$', ActivitiesViewSet.as_view({'get': 'retrieve', 'put': 'partial_update'})),
    url(r'^/(?P<activity_pk>\d+)/calendars/?$', ChronogramsViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/(?P<activity_pk>\d+)/calendars/(?P<calendar_pk>\d+)/?$', ChronogramsViewSet.as_view({
       'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})),
    # url(r'^/(?P<pk>\d+)/calendars/?$',ActivitiesViewSet.as_view({'post':'create_calendar',\
    # 	                            'put': 'update_calendar','get':'get_calendars','delete':'delete_calendar'})),

    url(r'^/(?P<pk>\d+)/publish/?$', ActivitiesViewSet.as_view({'put': 'publish'})),
    url(r'^/(?P<activity_pk>\d+)/gallery/?$', ActivityPhotosViewSet.as_view({'post': 'create'})),
    url(r'^/(?P<activity_pk>\d+)/gallery/(?P<gallery_pk>\d+)/?$', ActivityPhotosViewSet.as_view({'delete': 'destroy'})),

    url(r'^/info/?$', ActivitiesViewSet.as_view({'get': 'general_info'})),
    url(r'^/tags/?$', TagsViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^/categories/?$', CategoriesViewSet.as_view({'get': 'list'})),
    url(r'^/subcategories/?$', SubCategoriesViewSet.as_view({'get': 'list'})),
)