from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from orders.models import Refund, Order, Assistant
from orders.tasks import SendEMailStudentRefundTask, SendEmailOrganizerRefundTask


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_title', 'status')
    list_filter = ('status',)
    raw_id_fields = ('calendar', 'student', 'payment')

    def name(self, obj):
        return obj.student.user.get_full_name()

    def activity_title(self, obj):
        return obj.calendar.activity.title


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    raw_id_fields = ('order',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('username', 'order', 'assistant', 'status')
    readonly_fields = ('created_at',)
    actions = ['set_decline', 'set_approved']

    def username(self, obj):
        return obj.user.username

    def set_declined(self, request, queryset):
        queryset.update(status=Refund.DECLINED_STATUS)
        task = SendEMailStudentRefundTask()

        for refund in queryset:
            task.delay(refund.id)
    set_declined.short_description = _('Rechazar refunds seleccionado/s')

    def set_approved(self, request, queryset):
        send_email_student = SendEMailStudentRefundTask()
        send_email_organizer = SendEmailOrganizerRefundTask()

        for refund in queryset:
            refund.status = Refund.APPROVED_STATUS
            refund.save(update_fields=['status'])
            send_email_student.delay(refund.id)
            send_email_organizer.delay(refund.id)
    set_approved.short_description = _('Aprobar refunds seleccionado/s')
