from rest_framework import serializers

from referrals.models import Coupon


class CouponSerialzer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
