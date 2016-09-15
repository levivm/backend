from celery import group, chain

from django.contrib import admin

from balances.models import Withdrawal, BalanceLog
from balances.tasks import UpdateWithdrawalLogsStatusTask, NotifyWithdrawalOrganizerTask,\
                            CalculateOrganizerBalanceTask


@admin.register(BalanceLog)
class BalanceLogAdmin(admin.ModelAdmin):
    list_display = ['organizer', 'calendar_initial_date', 'activity_title', 'status']
    search_fields = ['calendar__id', 'organizer__name']

    def calendar_initial_date(self, obj):
        return obj.order.calendar.initial_date

    def activity_title(self, obj):
        return obj.order.calendar.activity.title


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    actions = ['mark_as_approved', 'mark_as_declined']
    list_display = ('id', 'status', 'amount', 'date')
    list_filter = ['status']

    def mark_as_approved(self, request, queryset):
        rows_updated = queryset.update(status='approved')
        self.message_user(request, 'Aprobado/s %s withdrawal satisfactoriamente.' % rows_updated)
        withdrawals_id = [w.id for w in queryset]

        update_task = UpdateWithdrawalLogsStatusTask()
        new_status = BalanceLog.STATUS_WITHDRAWN
        update_task.delay(withdrawal_ids=withdrawals_id, status=new_status)

        notify_task = NotifyWithdrawalOrganizerTask()
        group(*[notify_task.s(withdrawal_id=_id, status='approved') for _id in withdrawals_id])()
    mark_as_approved.short_description = 'Aprobar los withdrawal seleccionados'

    def mark_as_declined(self, request, queryset):

        rows_updated = queryset.update(status='declined')
        self.message_user(request, 'Rechazado/s %s withdrawal satisfactoriamente.' % rows_updated)
        withdrawals_id = [w.id for w in queryset]

        organizer = queryset[0].organizer

        update_task = UpdateWithdrawalLogsStatusTask()
        new_balancelog_status = BalanceLog.STATUS_AVAILABLE

        calculate_organizer_balance_task = CalculateOrganizerBalanceTask()

        chain(
            update_task.si(withdrawal_ids=withdrawals_id, status=new_balancelog_status),
            calculate_organizer_balance_task.si(organizer_ids=[organizer.id]),
        )()

        notify_task = NotifyWithdrawalOrganizerTask()
        group(*[notify_task.s(withdrawal_id=_id, status='declined') for _id in withdrawals_id])()
    mark_as_declined.short_description = 'Rechazar los withdrawal seleccionados'
