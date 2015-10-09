from django.conf.urls import url

from .views import OrdersViewSet

urlpatterns = [
    url(
        regex=r'^activities/(?P<activity_pk>\d+)/orders/?$',
        view=OrdersViewSet.as_view({'get': 'list_by_activity', 'post': 'create'}),
        name='create_or_list_by_activity'
    ),

    url(
        regex=r'^orders/(?P<order_pk>\d+)/?$',
        view=OrdersViewSet.as_view({'get': 'retrieve'}),
        name='retrieve'
    ),

    url(
        regex=r'^students/(?P<student_pk>\d+)/orders/?$',
        view=OrdersViewSet.as_view({'get': 'list_by_student'}),
        name='list_by_student'
    ),

    url(
        r'^organizers/(?P<organizer_pk>\d+)/orders/?$',
        OrdersViewSet.as_view({'get': 'list_by_organizer'}),
        name='list_by_organizer'
    ),
]
