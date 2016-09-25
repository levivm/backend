from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from utils.paginations import SmallResultsSetPagination
from utils.permissions import IsOrganizer
from .models import BalanceLog
from .serializers import WithdrawSerializer
from .tasks import CalculateOrganizerBalanceTask, NotifyWithdrawalRequestOrganizerTask


class BalanceRetrieveView(APIView):
    permission_classes = (IsAuthenticated, IsOrganizer)

    def get(self, request):
        balance = request.user.organizer_profile.balance
        data = {
            'available': balance.available,
            'unavailable': balance.unavailable,
        }
        return Response(data)


class WithdrawalListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsOrganizer)
    serializer_class = WithdrawSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return self.request.user.organizer_profile.withdrawals.order_by('-date')

    def create(self, request, *args, **kwargs):
        organizer = request.user.organizer_profile
        data = {
            'organizer': organizer.id,
            'logs': organizer.balance_logs.available().values_list('id', flat=True),
            'amount': organizer.balance.available
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        withdrawal = serializer.save()

        organizer.balance_logs.available().update(status=BalanceLog.STATUS_REQUESTED)
        calculate_organizer_balance_task = CalculateOrganizerBalanceTask()
        calculate_organizer_balance_task.delay([organizer.id])

        notify_organizer_request_task = NotifyWithdrawalRequestOrganizerTask()
        notify_organizer_request_task.delay(withdrawal.id)

        headers = self.get_success_headers(serializer.data)
        data_response = serializer.data
        data_response.update({
            'new_available_amount': 0
        })
        return Response(data_response, status=status.HTTP_201_CREATED, headers=headers)
