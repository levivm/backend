from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from orders.models import Refund
from orders.tasks import SendEMailStudentRefundTask


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    actions = ['set_decline']

    def set_decline(self, request, queryset):
        queryset.update(status=Refund.DECLINED_STATUS)
        task = SendEMailStudentRefundTask()

        for obj in queryset:
            task.delay(obj.id)
    set_decline.short_description = _('Rechazar refunds seleccionado/s')
