from rest_framework import serializers

from balances.models import Withdraw


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
