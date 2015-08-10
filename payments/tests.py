import json

from rest_framework import status

from orders.models import Order
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


    #AQUI VA TEST test_payu_confirmation_url_transaction_rejected

    # def test_payu_confirmation_url_transaction_declined(self):
    #     client = self.get_student_client()
    #     response = client.post(self.url, json.dumps(self.get_data()), content_type='application/json')
    #     order_id = response.data['id']
    #     order = Order.objects.get(id=order_id)
    #     self.assertFalse(order.enroll)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_DECLINED_CODE
    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     order = Order.objects.get(id=order_id)
    #     self.assertFalse(order.enroll)
    #     #Necesitamos determinar que va pasar cuando el pago es rechazado
    #     #Tal vez enviar un correo
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)


    # def test_payu_confirmation_url_transaction_approved(self):
    #     client = self.get_student_client()
    #     response = client.post(self.url, json.dumps(self.get_data()), content_type='application/json')
    #     order_id = response.data['id']
    #     order = Order.objects.get(id=order_id)
    #     self.assertFalse(order.enroll)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_APPROVED_CODE
    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     order = Order.objects.get(id=order_id)
    #     self.assertTrue(order.enroll)
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

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
