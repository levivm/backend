from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Payment
from .tasks import SendPaymentEmailTask
from orders.models import Order
from rest_framework import status
from activities.utils import PaymentUtil



# Create your views here.







class PayUNotificationPayment(APIView):

    def _run_transaction_declined_task(self,order,data):
        order.change_status(Order.ORDER_DECLINED_STATUS)
        error = data.get('response_message_pol')
        task_data={
            'transaction_error':PaymentUtil.RESPONSE_CODE_NOTIFICATION_URL\
                                        .get(error,'Error')
        }
        
        task = SendPaymentEmailTask()
        task.apply_async((order.id,),task_data, countdown=4)


    def post(self, request, *args, **kwargs):

        #The responses code: http://developers.payulatam.com/es/web_checkout/variables.html
        
        data   = request.POST
        transaction_status = data.get('state_pol')
        transaction_id = data.get('transaction_id')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        order = payment.order

        if   transaction_status == settings.TRANSACTION_APPROVED_CODE:
            
            if order.status == Order.ORDER_PENDING_STATUS:
                order.change_status(Order.ORDER_APPROVED_STATUS)
                task = SendPaymentEmailTask()
                task.apply_async((order.id,), countdown=4)

            
        elif transaction_status == settings.TRANSACTION_DECLINED_CODE:
            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_declined_task(order,data)
                # error = data.get('response_message_pol')
                # task_data={
                #     'transaction_error':PaymentUtil.RESPONSE_CODE_NOTIFICATION_URL\
                #                                 .get(error,'Error')
                # }
                
                # task = SendPaymentEmailTask()
                # task.apply_async((order.id,),task_data, countdown=4)
                #enviar correo de pago rechazado

                
            pass

        elif transaction_status == settings.TRANSACTION_EXPIRED_CODE:
            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_declined_task(order,data)
                # order.delete()
                #enviar correo que orden expiro

        return Response(status=status.HTTP_200_OK)

