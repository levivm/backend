from django.conf.urls import url

from organizers.views import InstructorViewSet, ActivityInstructorViewSet, OrganizerBankInfoViewSet
from .views import signup, OrganizerViewSet, OrganizerInstructorViewSet, OrganizerLocationViewSet, \
    OrganizerBankInfoChoicesViewSet

urlpatterns = [
    url(r'^organizers/signup/$', signup),
    url(r'^organizers/(?P<organizer_pk>\d+)/?$',
        OrganizerViewSet.as_view({'put': 'partial_update', 'get': 'retrieve'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/activities/?$', OrganizerViewSet.as_view({'get': 'activities'})),
    # url(r'^(?P<pk>\d+)/locations/?$', OrganizerViewSet.as_view({'post':'set_location'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/locations/?$', OrganizerLocationViewSet.as_view({'post': 'set_location'})),
    url(r'^organizers/(?P<organizer_pk>\d+)/instructors/?$',
        OrganizerInstructorViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^instructors/(?P<pk>\d+)/?$', InstructorViewSet.as_view({'put': 'update', 'delete': 'destroy'})),
    url(r'^activities/(?P<activity_pk>\d+)/instructors/?$',
        ActivityInstructorViewSet.as_view({'get': 'list', 'post': 'create'})),
    url(r'^activities/(?P<activity_pk>\d+)/instructors/(?P<pk>\d+)?$',
        ActivityInstructorViewSet.as_view({'put': 'update', 'delete': 'destroy'})),

    # {% url organizers:bank_info_api %}
    url(
        regex=r'^organizers/bankinfo/?$',
        view=OrganizerBankInfoViewSet.as_view({'post': 'create', 'get': 'retrieve', 'put': 'partial_update'}),
        name='bank_info_api',
    ),

    # {% url organizers:bank_choices %}
    url(
        regex=r'^bankinfo/choices/?$',
        view=OrganizerBankInfoChoicesViewSet.as_view({'get': 'choices'}),
        name='bank_choices',
    ),
]
