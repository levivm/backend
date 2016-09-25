from django.contrib import admin

from payments.models import Fee, Payment
from utils.mixins import OperativeModelAdminMixin


@admin.register(Payment)
class PaymentAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('order_num', 'order_email', 'date')
    list_filter = ('date',)
    search_fields = ['transaction_id']
    operative_readonly_fields = {'payment_type', 'card_type', 'transaction_id', 'last_four_digits',
                                 'response'}

    def order_num(self, obj):
        return obj.order.id

    def order_email(self, obj):
        return obj.order.student.user.email


@admin.register(Fee)
class FeeAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('type', 'amount')
    operative_readonly_fields = {'amount', 'type'}
