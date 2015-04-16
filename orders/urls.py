from django.conf.urls import patterns, url

from .views import OrdersViewSet

urlpatterns = patterns('',
    url(r'^activities/(?P<activity_pk>\d+)/orders/?$', OrdersViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^orders/(?P<order_id>\d+)/?$', OrdersViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
)