from django.conf.urls import url

from messages.views import ListAndCreateOrganizerMessageView, RetrieveDestroyOrganizerMessageView,\
                            ReadOrganizerMessageView

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
        view=RetrieveDestroyOrganizerMessageView.as_view(),
        name='retrieve_and_destroy',
    ),


    # messages:update  - api/messages/<id>/read/
    url(
        regex=r'^(?P<organizer_message>\d+)/read/?$',
        view=ReadOrganizerMessageView.as_view(),
        name='mark_as_read',
    ),


]
