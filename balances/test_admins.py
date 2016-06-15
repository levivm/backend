import mock
from django.contrib.admin.sites import AdminSite
from rest_framework.test import APITestCase

from balances.admin import WithdrawalAdmin
from balances.factories import WithdrawalFactory
from balances.models import Withdrawal


class WithdrawalAdminTest(APITestCase):
    def setUp(self):
        self.admin = WithdrawalAdmin(Withdrawal, AdminSite())
        WithdrawalFactory.create_batch(3, status='pending')

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

        update.assert_called_with(withdrawal_ids=[withdrawal.id for withdrawal in queryset])
        notify.assert_has_calls(calls=calls, any_order=True)

    @mock.patch('balances.tasks.NotifyWithdrawalOrganizerTask.s')
    @mock.patch('balances.admin.WithdrawalAdmin.message_user')
    def test_mark_as_declined(self, message_user, notify):
        request = mock.Mock()
        queryset = Withdrawal.objects.all()

        self.admin.mark_as_declined(request, queryset)
        self.assertEqual(list(queryset.values_list('status', flat=True)),
                         ['declined' for _ in range(3)])

        calls = [mock.call(withdrawal_id=withdrawal.id, status='declined') for withdrawal in
                 queryset]
        notify.assert_has_calls(calls=calls, any_order=True)
