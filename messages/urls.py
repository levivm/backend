from django.conf.urls import url

from messages.views import ListAndCreateOrganizerMessageView, DetailOrganizerMessageView

urlpatterns = [
    # messages:list_and_create - api/messages/
    url(
        regex=r'^$',
        view=ListAndCreateOrganizerMessageView.as_view(),
        name='list_and_create',
    ),

    # messages:detail  - api/messages/<id>/
    url(
        regex=r'^(?P<pk>\d+)/?$',
        view=DetailOrganizerMessageView.as_view(),
        name='detail',
    )
]
