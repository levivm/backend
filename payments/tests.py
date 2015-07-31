import json
from django.conf import settings
from django.contrib.auth.models import User
from django.http.request import HttpRequest
from requests.api import post
from rest_framework import status
from activities.models import Activity
from orders.models import Order
from orders.views import OrdersViewSet
from payments.models import Payment
from utils.tests import BaseViewTest


class PaymentLogicTest(BaseViewTest):
    url = '/api/activities/1/orders'
    view = OrdersViewSet

    def get_data(self):
        return {
            'token': self.get_token(),
            'buyer': {
                'name': 'APPROVED',
                'email': 'test@payulatam.com',
            },
            'card_association': 'visa',
            'chronogram': 1,
            'quantity': 1,
            'amount': 5000,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }

    def get_token(self):
        data = {
            'language': 'es',
            'command': 'CREATE_TOKEN',
            'merchant': {
              'apiLogin': settings.PAYU_API_LOGIN,
              'apiKey': settings.PAYU_API_KEY,
            },
            'creditCardToken': {
                'payerId': self.STUDENT_ID,
                'number': '4111111111111111',
                'expirationDate': '2016/09',
                'name': 'test',
                'paymentMethod': 'VISA',
            },
        }
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        result = post(url=settings.PAYU_URL, data=json.dumps(data), headers=headers)
        result = result.json()
        return result['creditCardToken']['creditCardTokenId']

    def test_creditcard_denied(self):
        client = self.get_student_client()
        data = self.get_data()
        data['buyer']['name'] = 'REJECTED'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(payments.count(), 0)
        self.assertEqual(orders.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'ERROR', response.content)

    def test_creditcard_approved(self):
        client = self.get_student_client()
        response = client.post(self.url, json.dumps(self.get_data()), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(payments.count(), 1)
        self.assertEqual(orders.count(), 2)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
