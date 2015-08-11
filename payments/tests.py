import json

from rest_framework import status

from orders.models import Order, ORDER_APPROVED_STATUS,ORDER_CANCELLED_STATUS,\
        ORDER_PENDING_STATUS
from orders.views import OrdersViewSet
from payments.models import Payment
from utils.tests import BaseViewTest
from django.conf import settings


class PaymentLogicTest(BaseViewTest):
    url = '/api/activities/1/orders'
    payu_callback_url = '/api/payments/notification/'
    view = OrdersViewSet

    def test_creditcard_declined(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'DECLINED'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(payments.count(), 1)
        self.assertEqual(orders.count(), 1)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(b'Su tarjeta ha sido rechazada', response.content)



    def test_payu_confirmation_url_transaction_does_not_exist(self):
        client = self.get_student_client()
        data = {
            'transaction_id':'invalid_id',
            'state_pol':settings.TRANSACTION_DECLINED_CODE
        }
        payu_callback_response = client.post(self.payu_callback_url,data=data)
        self.assertEqual(payu_callback_response.status_code,status.HTTP_404_NOT_FOUND)


    def test_payu_confirmation_url_transaction_expired(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment  = Payment.objects.get(order=order)
        data = {
            'transaction_id':payment.transaction_id,
            'state_pol':settings.TRANSACTION_EXPIRED_CODE
        }
        payu_callback_response = client.post(self.payu_callback_url,data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(),0)
        self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)


    def test_payu_confirmation_url_transaction_declined(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment  = Payment.objects.get(order=order)
        data = {
            'transaction_id':payment.transaction_id,
            'state_pol':settings.TRANSACTION_DECLINED_CODE
        }
        payu_callback_response = client.post(self.payu_callback_url,data=data)
        orders = Order.objects.filter(id=order_id)
        self.assertEqual(orders.count(),0)
        self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)


    def test_payu_confirmation_url_transaction_approved(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        order_id = response.data['id']
        order = Order.objects.get(id=order_id)
        payment  = Payment.objects.get(order=order)
        data = {
            'transaction_id':payment.transaction_id,
            'state_pol':settings.TRANSACTION_APPROVED_CODE
        }
        payu_callback_response = client.post(self.payu_callback_url,data=data)
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.status,ORDER_APPROVED_STATUS)
        self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

    def test_creditcard_approved(self):
        client = self.get_student_client()
        response = client.post(self.url, json.dumps(self.get_payment_data()), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payments.count(), 2)
        self.assertEqual(orders.count(), 2)
        last_order = orders.latest('pk')
        self.assertEqual(last_order.status, 'approved')
        self.assertEqual(last_order.assistants.count(), 1)

    def test_creditcard_pending(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['buyer']['name'] = 'PENDING'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(payments.count(), 2)
        self.assertEqual(orders.count(), 2)
        last_order = orders.latest('pk')
        self.assertEqual(last_order.status, 'pending')
        self.assertEqual(last_order.assistants.count(), 1)

    def test_creditcard_error(self):
        client = self.get_student_client()
        data = self.get_payment_data()
        data['token'] = '1234567890'
        response = client.post(self.url, json.dumps(data), content_type='application/json')
        payments = Payment.objects.all()
        orders = Order.objects.all()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(payments.count(), 1)
        self.assertEqual(orders.count(), 1)
        self.assertIn(b'ERROR', response.content)
