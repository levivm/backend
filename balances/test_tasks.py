from datetime import timedelta

import factory
from django.utils.timezone import now
from rest_framework.test import APITestCase

from activities.factories import CalendarFactory
from balances.factories import BalanceLogFactory, BalanceFactory
from balances.models import BalanceLog, Balance
from balances.tasks import BalanceLogToAvailableTask, CalculateOrganizerBalanceTask
from orders.factories import OrderFactory
from organizers.factories import OrganizerFactory


class BalanceLogToAvailableTaskTest(APITestCase):
    def setUp(self):
        self.organizer = OrganizerFactory()

    def test_balance_log_available(self):
        last_week = now() - timedelta(days=5)
        calendar = CalendarFactory(activity__organizer=self.organizer, initial_date=last_week)
        balance_log = BalanceLogFactory(organizer=self.organizer, calendar=calendar)

        task = BalanceLogToAvailableTask()
        result = task.delay()

        self.assertEqual(BalanceLog.objects.get(id=balance_log.id).status, 'available')
        self.assertEqual(result.result, [self.organizer.id])

    def test_balance_not_yet_available(self):
        calendar = CalendarFactory(activity__organizer=self.organizer, initial_date=now())
        balance_log = BalanceLogFactory(organizer=self.organizer, calendar=calendar)

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
        OrderFactory.create_batch(
            size=3,
            calendar=available_calendar,
            status='approved',
            amount=factory.Iterator([20000, 30000]))

        unavailable_calendar = CalendarFactory(activity__organizer=self.organizer)
        OrderFactory.create_batch(
            size=4,
            calendar=unavailable_calendar,
            status='approved',
            amount=factory.Iterator([20000, 30000]))

        BalanceLogFactory.create_batch(
            size=2,
            calendar=factory.Iterator([available_calendar, unavailable_calendar]),
            organizer=self.organizer,
            status=factory.Iterator(['available', 'unavailable']))

        task = CalculateOrganizerBalanceTask()
        task.delay(organizer_ids=[self.organizer.id])

        balance = Balance.objects.get(id=self.organizer.balance.id)
        self.assertEqual(balance.available, 70000)
        self.assertEqual(balance.unavailable, 100000)
