from celery.task import Task
from dateutil.relativedelta import relativedelta, MO
from django.utils.timezone import now

from balances.models import BalanceLog, Withdrawal
from balances.serializers import WithdrawSerializer
from organizers.models import Organizer
from utils.tasks import SendEmailTaskMixin


class BalanceLogToAvailableTask(Task):

    def run(self, *args, **kwargs):
        last_monday = now() + relativedelta(weekday=MO(-1), hour=0, minute=0)
        last_week_monday = last_monday - relativedelta(weeks=1)
        balance_logs = BalanceLog.objects.unavailable(
            order__calendar__initial_date__range=(last_week_monday, last_monday),
            organizer__type=Organizer.ORGANIZER_NORMAL)

        result = []
        if balance_logs:
            result = list(set(balance_logs.values_list('organizer_id', flat=True)))
            balance_logs.update(status='available')

        return result

class CalculateOrganizerBalanceTask(Task):

    def run(self, organizer_ids=[], *args, **kwargs):
        organizers = Organizer.objects.filter(id__in=organizer_ids)
        for organizer in organizers:
            organizer.balance.available = self.calculate_amount(organizer=organizer,
                                                                status='available')
            organizer.balance.unavailable = self.calculate_amount(organizer=organizer,
                                                                  status='unavailable')
            organizer.balance.save()

    def calculate_amount(self, organizer, status):
        balance_logs = organizer.balance_logs.filter(status=status)
        return sum([log.order.total_net for log in balance_logs])


class BalanceLogSpecialToAvailableTask(Task):

    def run(self, *args, **kwargs):
        last_day_month = now().date().replace(day=1)
        first_day_month = last_day_month - relativedelta(months=1)

        balance_logs = BalanceLog.objects.unavailable(
            created_at__range=(first_day_month, last_day_month),
            organizer__type=Organizer.ORGANIZER_SPECIAL)

        result = []
        if balance_logs:
            result = list(set(balance_logs.values_list('organizer_id', flat=True)))
            balance_logs.update(status='available')

        return result


class AutoWithdrawalSpecialOrganizerTask(Task):

    def run(self, *args, **kwargs):
        organizers = Organizer.objects.filter(type=Organizer.ORGANIZER_SPECIAL)

        for organizer in organizers:
            data = {
                'organizer': organizer.id,
                'logs': organizer.balance_logs.available().values_list('id', flat=True),
                'amount': organizer.balance.available
            }

            if data['amount'] > 0:
                serializer = WithdrawSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()

        return [organizer.id for organizer in organizers]


class UpdateWithdrawalLogsStatusTask(Task):

    def run(self, withdrawal_ids=None, status=None, *args, **kwargs):
        self.withdrawals = Withdrawal.objects.filter(id__in=withdrawal_ids)

        for withdrawal in self.withdrawals:
            BalanceLog.objects.filter(id__in=withdrawal.logs.values_list('id', flat=True))\
                .update(status=status)
 
class NotifyWithdrawalOrganizerTask(SendEmailTaskMixin):

    def run(self, withdrawal_id, status, *args, **kwargs):
        self.withdrawal = Withdrawal.objects.get(id=withdrawal_id)
        self.template_name = 'balances/email/notify_withdraw.html'
        self.emails = [self.withdrawal.organizer.user.email]
        self.subject = 'Notificación acerca de tu retiro'
        self.global_context = self.get_context_data()
        return super(NotifyWithdrawalOrganizerTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {}
