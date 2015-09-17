import json
from rest_framework import status

from orders.models import Order
from orders.views import OrdersViewSet
from payments.models import Payment
from utils.tests import BaseViewTest
from django.conf import settings
from .tasks import SendPaymentEmailTask
from utils.models import EmailTaskRecord
from activities.utils import PaymentUtil
from django.utils.translation import ugettext_lazy as _





# class PaymentLogicTest(BaseViewTest):
#     url = '/api/activities/1/orders'
#     payu_callback_url = '/api/payments/notification/'
#     view = OrdersViewSet
#     ORDER_ID  = 1

#     def setUp(self):
#         settings.CELERY_ALWAYS_EAGER = True
#     def tearDown(self):
#         settings.CELERY_ALWAYS_EAGER = False

#     def get_payments_count(self):
#         return Payment.objects.count()

#     def get_orders_count(self):
#         return Order.objects.count()

#     def test_payu_confirmation_url_transaction_does_not_exist(self):
#         client = self.get_student_client()
#         data = {
#             'transaction_id':'invalid_id',
#             'state_pol':settings.TRANSACTION_DECLINED_CODE
#         }
#         payu_callback_response = client.post(self.payu_callback_url,data=data)
#         self.assertEqual(payu_callback_response.status_code,status.HTTP_404_NOT_FOUND)

#     def test_payu_confirmation_url_transaction_expired(self):

#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['buyer']['name'] = 'PENDING'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         order_id = response.data['id']
#         order = Order.objects.get(id=order_id)
#         payment  = Payment.objects.get(order=order)
#         data = {
#             'transaction_id':payment.transaction_id,
#             'state_pol':settings.TRANSACTION_EXPIRED_CODE,
#             'payment_method_type':settings.CC_METHOD_PAYMENT_ID
#         }
#         payu_callback_response = client.post(self.payu_callback_url,data=data)
#         orders = Order.objects.filter(id=order_id)
#         self.assertEqual(orders.count(),0)
#         self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

#     def test_payu_confirmation_url_transaction_declined(self):
#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['buyer']['name'] = 'PENDING'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         order_id = response.data['id']
#         order = Order.objects.get(id=order_id)
#         payment  = Payment.objects.get(order=order)
#         data = {
#             'transaction_id':payment.transaction_id,
#             'state_pol':settings.TRANSACTION_DECLINED_CODE,
#             'payment_method_type':settings.CC_METHOD_PAYMENT_ID

#         }
#         payu_callback_response = client.post(self.payu_callback_url,data=data)
#         orders = Order.objects.filter(id=order_id)
#         self.assertEqual(orders.count(),0)
#         self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)


#     def test_payu_confirmation_url_transaction_approved(self):
#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['buyer']['name'] = 'PENDING'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         order_id = response.data['id']
#         order = Order.objects.get(id=order_id)
#         payment  = Payment.objects.get(order=order)
#         data = {
#             'transaction_id':payment.transaction_id,
#             'state_pol':settings.TRANSACTION_APPROVED_CODE,
#             'payment_method_type':settings.CC_METHOD_PAYMENT_ID

#         }
#         payu_callback_response = client.post(self.payu_callback_url,data=data)
#         order = Order.objects.get(id=order_id)
#         self.assertEqual(order.status,Order.ORDER_APPROVED_STATUS)
#         self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)


#     def test_creditcard_declined(self):
#         payments_count = self.get_payments_count()
#         orders_count = self.get_orders_count()
#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['buyer']['name'] = 'DECLINED'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         self.assertEqual(self.get_payments_count(), payments_count)
#         self.assertEqual(self.get_orders_count(), orders_count)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn(b'Su tarjeta ha sido rechazada', response.content)

#     def test_creditcard_approved(self):
#         payments_count = self.get_payments_count()
#         orders_count = self.get_orders_count()
#         client = self.get_student_client()
#         response = client.post(self.url, json.dumps(self.get_payment_data()), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(self.get_payments_count(), payments_count + 1)
#         self.assertEqual(self.get_orders_count(), orders_count + 1)
#         last_order = Order.objects.latest('pk')
#         self.assertEqual(last_order.status, 'approved')
#         self.assertEqual(last_order.assistants.count(), 1)

#     def test_creditcard_pending(self):
#         payments_count = self.get_payments_count()
#         orders_count = self.get_orders_count()
#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['buyer']['name'] = 'PENDING'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(self.get_payments_count(), payments_count + 1)
#         self.assertEqual(self.get_orders_count(), orders_count + 1)
#         last_order = Order.objects.latest('pk')
#         self.assertEqual(last_order.status, 'pending')
#         self.assertEqual(last_order.assistants.count(), 1)

#     def test_creditcard_error(self):
#         payments_count = self.get_payments_count()
#         orders_count = self.get_orders_count()
#         client = self.get_student_client()
#         data = self.get_payment_data()
#         data['token'] = '1234567890'
#         response = client.post(self.url, json.dumps(data), content_type='application/json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertEqual(self.get_payments_count(), payments_count)
#         self.assertEqual(self.get_orders_count(), orders_count)
#         self.assertIn(b'ERROR', response.content)

#     def test_payment_approved_notification_email_task(self):
#         order = Order.objects.get(id=self.ORDER_ID)
#         order.change_status(Order.ORDER_APPROVED_STATUS)
#         task = SendPaymentEmailTask()
#         task_data = {
#             'payment_method':settings.CC_METHOD_PAYMENT_ID
#         }
#         result = task.apply_async((order.id,),task_data, countdown=4)
#         email_task = EmailTaskRecord.objects.get(task_id=result.id)
#         self.assertTrue(email_task.send)
#         self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])
#         orders = Order.objects.filter(id=self.ORDER_ID)
#         self.assertEqual(orders.count(), 1) 


#     def test_payu_declined_notification_email_task(self):
#         order = Order.objects.get(id=self.ORDER_ID)
#         order.change_status(Order.ORDER_DECLINED_STATUS)
#         error_msg = PaymentUtil.RESPONSE_CODE_NOTIFICATION_URL\
#                                         .get('ENTITY_DECLINED','Error')
#         task_data={
#             'transaction_error':error_msg,
#             'payment_method':settings.CC_METHOD_PAYMENT_ID

#         }
#         task = SendPaymentEmailTask()
#         result = task.apply((order.id,),task_data, countdown=4)
#         email_task = EmailTaskRecord.objects.get(task_id=result.id)        
#         self.assertTrue(email_task.send)
#         expected_error = str(error_msg)
#         self.assertEqual(expected_error,email_task.data['error'])
#         self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])

#         orders = Order.objects.filter(id=self.ORDER_ID)
#         self.assertEqual(orders.count(), 0)




class PayUPSETest(BaseViewTest):
    # url = '/api/payments/pse'
    url = '/api/activities/1/orders'
    payu_callback_url = '/api/payments/notification/'
    ORDER_ID  = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def get_payments_count(self):
        return Payment.objects.count()

    def get_orders_count(self):
        return Order.objects.count()

    def test_pse_payment(self):
        client = self.get_student_client()
        data = json.dumps(self.get_payment_pse_data())
        response = client.post(self.url, data , content_type='application/json')
        print("RESPONSE ",response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"bank_url":"https://pse.todo1.com/', response.content)

    # def test_pse_payment_declined(self):
    #     client = self.get_student_client()
    #     data = self.get_payment_pse_data()
    #     data['buyer']['name'] = 'DECLINED'
    #     data = json.dumps(data)
    #     response = client.post(self.url, data , content_type='application/json')
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    # def test_payu_confirmation_url_pse_transaction_declined(self):
    #     client = self.get_student_client()
    #     data = self.get_payment_data()
    #     data['buyer']['name'] = 'PENDING'
    #     response = client.post(self.url, json.dumps(data), \
    #             content_type='application/json')
    #     order_id = response.data['id']
    #     order = Order.objects.get(id=order_id)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_DECLINED_CODE,
    #         'response_code_pol':settings.RESPONSE_CODE_POL_DECLINED,
    #         'payment_method_type':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     orders = Order.objects.filter(id=order_id)
    #     self.assertEqual(orders.count(),0)
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

    # def test_payu_confirmation_url_pse_transaction_pending(self):
    #     client = self.get_student_client()
    #     data = self.get_payment_data()
    #     data['buyer']['name'] = 'PENDING'
    #     response = client.post(self.url, json.dumps(data), content_type='application/json')
    #     order_id = response.data['id']
    #     order = Order.objects.get(id=order_id)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_PENDING_PSE_CODE,
    #         'payment_method_type':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     orders = Order.objects.filter(id=order_id)
    #     self.assertEqual(orders.count(), 1)
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

    # def test_payu_confirmation_url_pse_transaction_failed(self):
    #     client = self.get_student_client()
    #     data = self.get_payment_data()
    #     data['buyer']['name'] = 'PENDING'
    #     response = client.post(self.url, json.dumps(data), content_type='application/json')
    #     order_id = response.data['id']
    #     order = Order.objects.get(id=order_id)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_DECLINED_CODE,
    #         'response_code_pol':settings.RESPONSE_CODE_POL_FAILED,
    #         'payment_method_type':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     orders = Order.objects.filter(id=order_id)
    #     self.assertEqual(orders.count(),0)
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

    # def test_payu_confirmation_url_pse_transaction_approved(self):
    #     client = self.get_student_client()
    #     data = self.get_payment_data()
    #     data['buyer']['name'] = 'PENDING'
    #     response = client.post(self.url, json.dumps(data), content_type='application/json')
    #     order_id = int(response.data['id'])
    #     order = Order.objects.get(id=order_id)
    #     payment  = Payment.objects.get(order=order)
    #     data = {
    #         'transaction_id':payment.transaction_id,
    #         'state_pol':settings.TRANSACTION_APPROVED_CODE,
    #         'payment_method_type':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     payu_callback_response = client.post(self.payu_callback_url,data=data)
    #     order = Order.objects.get(id=order_id)
    #     self.assertEqual(order.status,Order.ORDER_APPROVED_STATUS)
    #     self.assertEqual(payu_callback_response.status_code,status.HTTP_200_OK)

    # def test_payment_pse_approved_notification_email_task(self):
    #     order = Order.objects.get(id=self.ORDER_ID)
    #     order.change_status(Order.ORDER_APPROVED_STATUS)
    #     task = SendPaymentEmailTask()
    #     task_data = {
    #         'payment_method':settings.PSE_METHOD_PAYMENT_ID
    #     }
    #     result = task.apply_async((order.id,),task_data, countdown=4)
    #     email_task = EmailTaskRecord.objects.get(task_id=result.id)
    #     self.assertTrue(email_task.send)
    #     self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])
    #     orders = Order.objects.filter(id=self.ORDER_ID)
    #     self.assertEqual(orders.count(), 1) 

    # def test_payment_pse_declined_notification_email_task(self):
    #     order = Order.objects.get(id=self.ORDER_ID)
    #     order.change_status(Order.ORDER_DECLINED_STATUS)
    #     error_msg = _('Transacción Rechazada')
    #     task_data={
    #         'transaction_error':error_msg,
    #         'payment_method':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     task = SendPaymentEmailTask()
    #     result = task.apply((order.id,),task_data, countdown=4)
    #     email_task = EmailTaskRecord.objects.get(task_id=result.id)
    #     expected_error = str(error_msg)
    #     self.assertTrue(email_task.send)
    #     self.assertEqual(expected_error,email_task.data['error'])
    #     self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])

    #     orders = Order.objects.filter(id=self.ORDER_ID)
    #     self.assertEqual(orders.count(), 0) 

    # def test_payment_pse_failed_notification_email_task(self):
    #     order = Order.objects.get(id=self.ORDER_ID)
    #     order.change_status(Order.ORDER_DECLINED_STATUS)
    #     error_msg = _('Transacción Fallida')
    #     task_data={
    #         'transaction_error':error_msg,
    #         'payment_method':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     task = SendPaymentEmailTask()
    #     result = task.apply((order.id,),task_data, countdown=4)
    #     email_task = EmailTaskRecord.objects.get(task_id=result.id)
    #     expected_error = str(error_msg)
    #     self.assertEqual(expected_error,email_task.data['error'])
    #     self.assertTrue(email_task.send)
    #     self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])
    #     orders = Order.objects.filter(id=self.ORDER_ID)
    #     self.assertEqual(orders.count(), 0) 


    # def test_payment_pse_pending_notification_email_task(self):
    #     order = Order.objects.get(id=self.ORDER_ID)
    #     order.change_status(Order.ORDER_PENDING_STATUS)
    #     error_msg  = 'Transacción pendiente, por favor revisar'
    #     error_msg += 'si el débito fue realizado en el banco.'
    #     error_msg  = _(error_msg)
    #     task_data={
    #         'transaction_error':error_msg,
    #         'payment_method':settings.PSE_METHOD_PAYMENT_ID

    #     }
    #     task = SendPaymentEmailTask()
    #     result = task.apply((order.id,),task_data, countdown=4)
    #     email_task = EmailTaskRecord.objects.get(task_id=result.id)        
    #     self.assertTrue(email_task.send)
    #     expected_error = str(error_msg)
    #     self.assertEqual(expected_error,email_task.data['error'])
    #     self.assertEqual(self.ORDER_ID,email_task.data['order']['id'])
    #     orders = Order.objects.filter(id=self.ORDER_ID)
    #     self.assertEqual(orders.count(), 1) 

class PaymentBankListTest(BaseViewTest):
    url = '/api/payments/pse/banks'

    def test_get_pse_bank_list(self):
        client = self.get_student_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"description":"BANCOLOMBIA QA"', response.content)

