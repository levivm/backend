from django.contrib import admin

from referrals.models import Referral, CouponType, Coupon, Redeem
from utils.mixins import OperativeModelAdminMixin


@admin.register(Referral)
class ReferralAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('referrer', 'referred')
    operative_readonly_fields = {'referred', 'referrer', 'ip_address'}


@admin.register(CouponType)
class CouponTypeAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'amount', 'type')
    list_filter = ('type',)
    operative_readonly_fields = {'name', 'amount', 'type'}


@admin.register(Coupon)
class CouponAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'coupon_type', 'created_at', 'valid_until')
    operative_readonly_fields = {'token', 'coupon_type', 'valid_until'}


@admin.register(Redeem)
class RedeemAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'student', 'coupon', 'used')
    list_filter = ('used',)
    operative_readonly_fields = {'student', 'coupon', 'used', 'redeem_at'}
