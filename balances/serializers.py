from rest_framework import serializers

from balances.models import Withdrawal


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
