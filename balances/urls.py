from django.conf.urls import url

from balances.views import BalanceRetrieveView, WithdrawListCreateView

urlpatterns = [

    # balances:balance - api/balances/balance
    url(
        regex=r'^balance/?$',
        view=BalanceRetrieveView.as_view(),
        name='balance',
    ),

    # balances:withdraw - api/balances/withdraw
    url(
        regex=r'^withdraw/?$',
        view=WithdrawListCreateView.as_view(),
        name='withdraw',
    ),
]
