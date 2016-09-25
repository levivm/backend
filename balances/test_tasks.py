from datetime import timedelta

import factory
import mock
from django.utils.timezone import now
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory
from balances.factories import BalanceLogFactory, BalanceFactory, WithdrawalFactory
from balances.models import BalanceLog, Balance, Withdrawal
from balances.tasks import BalanceLogToAvailableTask, CalculateOrganizerBalanceTask, \
    UpdateWithdrawalLogsStatusTask, NotifyWithdrawalOrganizerTask
from orders.factories import OrderFactory
from organizers.factories import OrganizerFactory
from utils.models import EmailTaskRecord


class BalanceLogToAvailableTaskTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()

    def test_balance_log_available(self):
        last_week = (now() - timedelta(days=5)).date()
        calendar = CalendarFactory(activity__organizer=self.organizer, initial_date=last_week)
        order = OrderFactory(calendar=calendar)
        balance_log = BalanceLogFactory(organizer=self.organizer, order=order)

        task = BalanceLogToAvailableTask()
        result = task.delay()

        self.assertEqual(BalanceLog.objects.get(id=balance_log.id).status, 'available')
        self.assertEqual(result.result, [self.organizer.id])

    def test_balance_not_yet_available(self):
        calendar = CalendarFactory(activity__organizer=self.organizer, initial_date=now().date())
        order = OrderFactory(calendar=calendar)
        balance_log = BalanceLogFactory(organizer=self.organizer, order=order)

        task = BalanceLogToAvailableTask()
        result = task.delay()

        self.assertEqual(BalanceLog.objects.get(id=balance_log.id).status, 'unavailable')
        self.assertEqual(result.result, [])


class CalculateOrganizerBalanceTaskTest(APITestCase):

    def setUp(self):
        self.organizer = OrganizerFactory()
        BalanceFactory(organizer=self.organizer)

    def test_calculate_balance(self):
        available_calendar = CalendarFactory(activity__organizer=self.organizer)
        available_orders = OrderFactory.create_batch(
            size=3,
            calendar=available_calendar,
            status='approved',
            fee=0,
            amount=factory.Iterator([20000, 30000]))

        unavailable_calendar = CalendarFactory(activity__organizer=self.organizer)
        unavailable_orders = OrderFactory.create_batch(
            size=4,
            calendar=unavailable_calendar,
            status='approved',
            fee=0,
            amount=factory.Iterator([20000, 30000]))

        status = [*['available'] * 3, *['unavailable'] * 4]

        BalanceLogFactory.create_batch(
            size=7,
            order=factory.Iterator([*available_orders, *unavailable_orders]),
            organizer=self.organizer,
            status=factory.Iterator(status))

        task = CalculateOrganizerBalanceTask()
        task.delay(organizer_ids=[self.organizer.id])

        balance = Balance.objects.get(id=self.organizer.balance.id)
        self.assertEqual(balance.available, 70000)
        self.assertEqual(balance.unavailable, 100000)


class UpdateWithdrawalLogsStatusTaskTest(APITestCase):

    def test_run(self):
        logs = BalanceLogFactory.create_batch(6, status='available')
        WithdrawalFactory(logs=logs[:3])
        WithdrawalFactory(logs=logs[3:])

        withdrawals = Withdrawal.objects.values_list('id', flat=True)
        task = UpdateWithdrawalLogsStatusTask()
        status = 'withdrawn'
        task.delay(withdrawal_ids=withdrawals, status=status)

        self.assertEqual(list(BalanceLog.objects.values_list('status', flat=True)),
                         ['withdrawn' for _ in range(6)])


class NotifyWithdrawalOrganizerTaskTest(APITestCase):

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_approved(self, send_mail):
        withdrawal = WithdrawalFactory()

        send_mail.return_value = [{
            'email': withdrawal.organizer.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = NotifyWithdrawalOrganizerTask()
        task_id = task.delay(withdrawal_id=withdrawal.id, status='approved')

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=withdrawal.organizer.user.email,
            status='sent',
            template_name='balances/email/notify_withdraw.html').exists())

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_declined(self, send_mail):
        withdrawal = WithdrawalFactory()

        send_mail.return_value = [{
            'email': withdrawal.organizer.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = NotifyWithdrawalOrganizerTask()
        task_id = task.delay(withdrawal_id=withdrawal.id, status='declined')

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=withdrawal.organizer.user.email,
            status='sent',
            template_name='balances/email/notify_withdraw.html').exists())
