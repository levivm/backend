from celery.task import Task
from dateutil.relativedelta import relativedelta, MO
from django.utils.timezone import now

from balances.models import BalanceLog, Balance
from organizers.models import Organizer


class BalanceLogToAvailableTask(Task):

    def run(self, *args, **kwargs):
        last_monday = now() + relativedelta(weekday=MO(-1), hour=0, minute=0)
        last_week_monday = last_monday - relativedelta(weeks=1)
        balance_logs = BalanceLog.objects.filter(
            status='unavailable',
            calendar__initial_date__range=(last_week_monday, last_monday))

        result = []
        if balance_logs:
            result = list(set(balance_logs.values_list('organizer_id', flat=True)))
            balance_logs.update(status='available')

        return result

class CalculateOrganizerBalanceTask(Task):

    def run(self, organizer_ids, *args, **kwargs):
        organizers = Organizer.objects.filter(id__in=organizer_ids)
        for organizer in organizers:
            organizer.balance.available = self.calculate_amount(organizer=organizer,
                                                                status='available')
            organizer.balance.unavailable = self.calculate_amount(organizer=organizer,
                                                                  status='unavailable')
            organizer.balance.save()

    def calculate_amount(self, organizer, status):
        balance_logs = organizer.balance_logs.filter(status=status)
        return sum([o.total_net for log in balance_logs for o in log.calendar.orders.available()])
