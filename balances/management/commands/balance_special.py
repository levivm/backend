from celery import chain

from django.core.management.base import BaseCommand

from balances.tasks import BalanceLogSpecialToAvailableTask, CalculateOrganizerBalanceTask, \
    AutoWithdrawalSpecialOrganizerTask


class Command(BaseCommand):
    help = 'Run the tasks for calculate balance'

    def handle(self, *args, **options):
        available_balance_task = BalanceLogSpecialToAvailableTask()
        calculate_balance_task = CalculateOrganizerBalanceTask()
        auto_withdrawal_task = AutoWithdrawalSpecialOrganizerTask()

        chain(
            available_balance_task.s(),
            calculate_balance_task.s(),
            auto_withdrawal_task.s(),
            calculate_balance_task.s()
        )()
