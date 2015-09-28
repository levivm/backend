from django.conf.urls import url
from referrals.views import InviteView, AcceptInvitation

urlpatterns = [
    # {% url referrals:invite %}
    url(
        regex=r'^invite/?$',
        view=InviteView.as_view(),
        name='invite'
    ),

    # {% url referrals:referrer %}
    url(
        regex=r'^r/(?P<referrer_code>\w+)/?$',
        view=AcceptInvitation.as_view(),
        name='referrer'
    ),
]