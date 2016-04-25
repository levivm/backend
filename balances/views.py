from rest_framework import status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from balances.serializers import WithdrawSerializer
from utils.paginations import SmallResultsSetPagination
from utils.permissions import IsOrganizer


class BalanceRetrieveView(APIView):
    permission_classes = (IsAuthenticated, IsOrganizer)

    def get(self, request):
        balance = request.user.organizer_profile.balance
        data = {
            'available': balance.available,
            'unavailable': balance.unavailable,
        }
        return Response(data)


class WithdrawListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsOrganizer)
    serializer_class = WithdrawSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return self.request.user.organizer_profile.withdraws.all()

    def create(self, request, *args, **kwargs):
        organizer = request.user.organizer_profile
        data = {
            'organizer': organizer.id,
            'logs': organizer.balance_logs.available().values_list('id', flat=True),
            'amount': organizer.balance.available,
        }
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
