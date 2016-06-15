from django.conf.urls import url

from balances.views import BalanceRetrieveView, WithdrawalListCreateView

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
        view=WithdrawalListCreateView.as_view(),
        name='withdraw',
    ),
]
