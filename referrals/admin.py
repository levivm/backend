from django.contrib import admin

from referrals.models import Referral, CouponType, Coupon, Redeem


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    pass


@admin.register(CouponType)
class CouponTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    pass


@admin.register(Redeem)
class RedeemAdmin(admin.ModelAdmin):
    pass
