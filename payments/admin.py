from django.contrib import admin

from payments.models import Fee, Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    pass


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    pass
