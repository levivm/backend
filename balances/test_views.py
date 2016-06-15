from django.core.urlresolvers import reverse
from rest_framework import status

from balances.factories import BalanceFactory, BalanceLogFactory, WithdrawalFactory
from utils.tests import BaseAPITestCase


class BalanceViewTest(BaseAPITestCase):

    def setUp(self):
        super(BalanceViewTest, self).setUp()
        BalanceFactory(organizer=self.organizer, available=1500000, unavailable=500000)
        self.url = reverse('balances:balance')

    def test_list(self):
        # Anonymous should get unauthorized 401
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should get forbidden 403
        response = self.student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should get the data 200
        response = self.organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'available': 1500000, 'unavailable': 500000})


class WithdrawalListCreateViewTest(BaseAPITestCase):

    def setUp(self):
        super(WithdrawalListCreateViewTest, self).setUp()
        self.url = reverse('balances:withdraw')
        self.logs = BalanceLogFactory.create_batch(size=3, organizer=self.organizer,
                                                   status='available')
        self.withdraw = WithdrawalFactory(organizer=self.organizer, logs=self.logs,
                                          amount=300000)
        BalanceFactory(organizer=self.organizer, available=300000)

    def test_create(self):
        # Anonymous should get unauthorized 401
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should get forbidden 403
        response = self.student_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer shouldn't be able create the withdraw 201
        response = self.organizer_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = {
            'amount': 300000,
            'logs': [log.id for log in self.logs],
            'organizer': self.organizer.id,
            'status': 'pending',
        }
        self.assertTrue(all(item in response.data.items() for item in data.items()))

    def test_list(self):
        # Anonymous should get unauthorized 401
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should get forbidden 403
        response = self.student_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should get the list
        response = self.organizer_client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertListEqual(response.data['results'], [{
            'id': self.withdraw.id,
            'organizer': self.organizer.id,
            'date': self.withdraw.date.isoformat()[:-6] + 'Z',
            'amount': 300000,
            'status': 'pending',
            'logs': [l.id for l in self.logs]
        }])
