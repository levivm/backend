from django.contrib import admin

from payments.models import Fee, Payment
from utils.mixins import OperativeModelAdminMixin


@admin.register(Payment)
class PaymentAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'payment_type', 'card_type', 'transaction_id', 'last_four_digits',
                                 'response'}


@admin.register(Fee)
class FeeAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'amount', 'name'}
