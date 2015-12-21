from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from orders.models import Refund, Order, Assistant
from orders.tasks import SendEMailStudentRefundTask, SendEmailOrganizerRefundTask


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    pass


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    pass


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at',)
    actions = ['set_decline', 'set_approved']

    def set_declined(self, request, queryset):
        queryset.update(status=Refund.DECLINED_STATUS)
        task = SendEMailStudentRefundTask()

        for refund in queryset:
            task.delay(refund.id)
    set_declined.short_description = _('Rechazar refunds seleccionado/s')

    def set_approved(self, request, queryset):
        queryset.update(status=Refund.APPROVED_STATUS)
        send_email_student = SendEMailStudentRefundTask()
        send_email_organizer = SendEmailOrganizerRefundTask()

        for refund in queryset:
            if refund.assistant is None:
                refund.order.change_status(Order.ORDER_CANCELLED_STATUS)
            else:
                refund.assistant.dismiss()

            send_email_student.delay(refund.id)
            send_email_organizer.delay(refund.id)
    set_approved.short_description = _('Aporbar refunds seleccionado/s')
