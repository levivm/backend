from celery import chain

from django.core.management.base import BaseCommand

from balances.tasks import BalanceLogToAvailableTask, CalculateOrganizerBalanceTask


class Command(BaseCommand):
    help = 'Run the tasks for calculate balance'

    def handle(self, *args, **options):
        available_balance_task = BalanceLogToAvailableTask()
        calculate_balance_task = CalculateOrganizerBalanceTask()

        chain(available_balance_task.s(), calculate_balance_task.s())()
