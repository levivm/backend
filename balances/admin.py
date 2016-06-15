from celery import group

from django.contrib import admin

from balances.models import Withdrawal
from balances.tasks import UpdateWithdrawalLogsStatusTask, NotifyWithdrawalOrganizerTask


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    actions = ['mark_as_approved', 'mark_as_declined']

    def mark_as_approved(self, request, queryset):
        rows_updated = queryset.update(status='approved')
        self.message_user(request, 'Aprobado/s %s withdrawal satisfactoriamente.' % rows_updated)
        withdrawals_id = [w.id for w in queryset]
        update_task = UpdateWithdrawalLogsStatusTask()
        update_task.delay(withdrawal_ids=withdrawals_id)
        notify_task = NotifyWithdrawalOrganizerTask()
        group(*[notify_task.s(withdrawal_id=_id, status='approved') for _id in withdrawals_id])()
    mark_as_approved.short_description = 'Aprobar los withdrawal seleccionados'

    def mark_as_declined(self, request, queryset):
        rows_updated = queryset.update(status='declined')
        self.message_user(request, 'Rechazado/s %s withdrawal satisfactoriamente.' % rows_updated)
        withdrawals_id = [w.id for w in queryset]
        notify_task = NotifyWithdrawalOrganizerTask()
        group(*[notify_task.s(withdrawal_id=_id, status='declined') for _id in withdrawals_id])()
    mark_as_declined.short_description = 'Rechazar los withdrawal seleccionados'
