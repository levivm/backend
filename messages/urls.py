from django.conf.urls import url

from messages.views import ListAndCreateOrganizerMessageView

urlpatterns = [
    # messages:list_and_create - api/messages/
    url(
        regex=r'^$',
        view=ListAndCreateOrganizerMessageView.as_view(),
        name='list_and_create',
    ),
]
