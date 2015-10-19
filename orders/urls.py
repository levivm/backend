from django.conf.urls import patterns, url

from .views import OrdersViewSet, RefundCreateReadView

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/orders/?$', 
    	OrdersViewSet.as_view({'get': 'list_by_activity','post': 'create'}),
    	name='create_or_list_by_activity'),

    url(r'^orders/(?P<order_pk>\d+)/?$', 
    	OrdersViewSet.as_view({'get': 'retrieve'}),
    	name='retrieve'),

    url(r'^students/(?P<student_pk>\d+)/orders/?$', 
    	OrdersViewSet.as_view({'get': 'list_by_student'}),
    	name='list_by_student'),

    url(r'^organizers/(?P<organizer_pk>\d+)/orders/?$', 
    	OrdersViewSet.as_view({'get': 'list_by_organizer'}),
    	name='list_by_organizer'),

    url(regex=r'^refunds/$',
        view=RefundCreateReadView.as_view(),
        name='refund_api'),
)