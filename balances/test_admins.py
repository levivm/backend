import mock
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase

from balances.admin import WithdrawalAdmin
from balances.factories import WithdrawalFactory, BalanceFactory
from balances.models import Withdrawal


class WithdrawalAdminTest(APITestCase):
    def setUp(self):
        self.admin = WithdrawalAdmin(Withdrawal, AdminSite())
        withdrawals = WithdrawalFactory.create_batch(3, status='pending')
        for withdrawal in withdrawals:
            BalanceFactory(organizer=withdrawal.organizer)


    @mock.patch('balances.tasks.NotifyWithdrawalOrganizerTask.s')
    @mock.patch('balances.tasks.UpdateWithdrawalLogsStatusTask.delay')
    @mock.patch('balances.admin.WithdrawalAdmin.message_user')
    def test_mark_as_approved(self, message_user, update, notify):
        request = mock.Mock()
        queryset = Withdrawal.objects.all()

        self.admin.mark_as_approved(request, queryset)
        self.assertEqual(list(queryset.values_list('status', flat=True)),
                         ['approved' for _ in range(3)])

        calls = [mock.call(withdrawal_id=withdrawal.id, status='approved') for withdrawal in
                 queryset]

        update.assert_called_with(withdrawal_ids=[withdrawal.id for withdrawal in queryset],
                                  status='withdrawn')
        notify.assert_has_calls(calls=calls, any_order=True)

    @mock.patch('balances.tasks.NotifyWithdrawalOrganizerTask.s')
    @mock.patch('balances.admin.WithdrawalAdmin.message_user')
    @mock.patch('balances.tasks.CalculateOrganizerBalanceTask.si')
    def test_mark_as_declined(self, balance_update, message_user, notify):
        request = mock.Mock()
        queryset = Withdrawal.objects.all()

        self.admin.mark_as_declined(request, queryset)
        self.assertEqual(list(queryset.values_list('status', flat=True)),
                         ['declined' for _ in range(3)])

        calls = [mock.call(withdrawal_id=withdrawal.id, status='declined') for withdrawal in
                 queryset]

        organizer = queryset[0].organizer

        balance_update.assert_called_with(organizer_ids=[organizer.id])

        notify.assert_has_calls(calls=calls, any_order=True)
