from django.conf.urls import url

from students.views import StudentViewSet, StudentActivitiesViewSet, WishListViewSet

urlpatterns = [
    url(r'^(?P<pk>\d+)/?$', StudentViewSet.as_view({'put': 'partial_update', 'get': 'retrieve'})),
    url(r'^(?P<pk>\d+)/activities/?$', StudentActivitiesViewSet.as_view({'get': 'retrieve'})),

    # {% activities:wish_list - api/students/wish_list/ %}
    url(
        regex=r'^wish_list/?$',
        view=WishListViewSet.as_view({'get': 'list', 'post': 'create'}),
        name='wish_list',
    )
]
