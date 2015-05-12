from django.conf.urls import patterns, url

from .views import OrdersViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/orders/?$', OrdersViewSet.as_view({'get': 'list_by_activity', 'post': 'create'})),
    url(r'^orders/(?P<order_pk>\d+)/?$', OrdersViewSet.as_view({'get': 'retrieve'})),
    url(r'^students/(?P<student_pk>\d+)/orders/?$', OrdersViewSet.as_view({'get': 'list_by_student'})),
)