from django.conf.urls import url
from referrals.views import InviteView, AcceptInvitation, GetCouponView

urlpatterns = [
    # {% url referrals:invite - api/referrals/invite %}
    # url(
    #     regex=r'^invite/?$',
    #     view=InviteView.as_view(),
    #     name='invite',
    # ),

    # {% url referrals:validate_coupon - api/referrals/coupons/<code> %}
    url(
        regex=r'^coupons/(?P<coupon_code>[\w\-]+)/?$',
        view=GetCouponView.as_view(),
        name='validate_coupon',
    ),

    # {% url referrals:referrer - api/referrals/<code> %}
    url(
        regex=r'^(?P<referrer_code>[\w\-]+)/?$',
        view=AcceptInvitation.as_view(),
        name='referrer',
    ),
]