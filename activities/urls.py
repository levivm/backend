from django.conf.urls import url

from activities.views import ActivitiesSearchView, ShareActivityEmailView, AutoCompleteView, \
    ActivityStatsView, ActivityViewsCounterView, CategoryRetrieveAPIView, ActivityFeatureListView
from .views import ActivitiesViewSet, CategoriesViewSet, \
    SubCategoriesViewSet, TagsViewSet, CalendarViewSet, \
    ActivityPhotosViewSet

urlpatterns = [
    url(r'^$', ActivitiesViewSet.as_view({'get': 'list', 'post': 'create'})),

    url(r'^(?P<activity_pk>\d+)/?$', ActivitiesViewSet.as_view({'get': 'retrieve', 'put': 'partial_update', 'delete':'destroy'})),
    url(r'^(?P<activity_pk>\d+)/calendars/?$', CalendarViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^(?P<activity_pk>\d+)/calendars/(?P<calendar_pk>\d+)/?$', CalendarViewSet.as_view({
       'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})),
    url(r'^(?P<activity_pk>\d+)/publish/?$', ActivitiesViewSet.as_view({'put': 'publish'})),
	url(r'^(?P<activity_pk>\d+)/unpublish/?$',ActivitiesViewSet.as_view({'put':'unpublish'})),
    url(r'^(?P<activity_pk>\d+)/locations/?$', ActivitiesViewSet.as_view({'put': 'set_location'})),
    url(r'^(?P<activity_pk>\d+)/gallery/cover/?$', ActivityPhotosViewSet.as_view({'post': 'set_cover_from_stock'}),name="set_cover_from_stock"),
    url(r'^(?P<activity_pk>\d+)/gallery/?$', ActivityPhotosViewSet.as_view({'post': 'create'}),name="upload_activity_photo"),
    url(r'^(?P<activity_pk>\d+)/gallery/(?P<gallery_pk>\d+)/?$', ActivityPhotosViewSet.as_view({'delete': 'destroy'}),name="delete_activity_photo"),




    url(r'^info/?$', ActivitiesViewSet.as_view({'get': 'general_info'})),
    url(r'^tags/?$', TagsViewSet.as_view({'get': 'list', 'post': 'create'  })),
    url(r'^categories/?$', CategoriesViewSet.as_view({'get': 'list'})),
    url(r'^subcategories/?$', SubCategoriesViewSet.as_view({'get': 'list'})),
    url(r'^subcategories/(?P<subcategory_id>\d+)/covers/?$', SubCategoriesViewSet.as_view({'get': 'get_pool_from_stock'}),name='get_covers_photos'),

    # {% url activities:category_detail %}
    url(regex=r'^categories/(?P<slug>[-\w]+)/?$',
        view=CategoryRetrieveAPIView.as_view(),
        name='category_detail'),

    # {% url activities:search %}
    url(regex=r'^search/?$',
        view=ActivitiesSearchView.as_view(),
        name='search',
    ),

    # {% url activities:share_email_activity %}
    url(
        regex=r'^(?P<activity_pk>\d+)/share/?$',
        view=ShareActivityEmailView.as_view(),
        name='share_email_activity',
    ),

    # {% url activities:auto_complete %}
    url(
       regex=r'^autocomplete/?$',
       view=AutoCompleteView.as_view(),
       name='auto_complete',
    ),

    # activities:stats - api/activities/<id>/stats
    url(
        regex=r'^(?P<activity_pk>\d+)/stats/?$',
        view=ActivityStatsView.as_view(),
        name='stats',
    ),

    # activities:views_counter - api/activities/<id>/views_counter
    url(
        regex=r'^(?P<pk>\d+)/views_counter/?$',
        view=ActivityViewsCounterView.as_view({'put': 'put'}),
        name='views_counter',
    ),

    # activities:featured - api/activities/featured
    url(
        regex=r'^featured/?$',
        view=ActivityFeatureListView.as_view(),
        name='featured'
    ),

]
