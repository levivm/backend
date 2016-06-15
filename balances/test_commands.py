import mock
from django.core.management import call_command
from rest_framework.test import APITestCase


class BalanceCommandTest(APITestCase):

    @mock.patch('balances.tasks.CalculateOrganizerBalanceTask.run')
    @mock.patch('balances.tasks.BalanceLogToAvailableTask.run')
    def test_handle(self, balance_subtask, calculate_subtask):
        balance_subtask.return_value = [1, 2, 3]
        calculate_subtask.return_value = None

        call_command('balance')
        calculate_subtask.assert_called_with([1,2,3])
