from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework import viewsets
from .models import Payment
from activities.models import Activity
from .tasks import SendPaymentEmailTask
from orders.models import Order
from rest_framework import status
from activities.utils import PaymentUtil
from orders.serializers import OrdersSerializer
import logging
import json



# Create your views here.
logger = logging.getLogger(__name__)

class PayUBankList(APIView):

    def get(self, request, *args, **kwargs):
        payment_util = PaymentUtil(request)
        bank_list = payment_util.get_bank_list()
        return Response(bank_list)


class PayUPSE(viewsets.ViewSet):

    def _get_activity(self,data):
        return get_object_or_404(Activity, id=data.get('activity'))

    def payment_response(self,request):
        logger.error("ESTO ES LA RESPUESTA DE PSE --------------------\n")
        logger.error(json.dumps(request.POST))
        logger.error("ESTO ES LA RESPUESTA DE PSE ////////------------\n")
        return Response(request.data)

    def post(self, request, *args, **kwargs):

        activity = self._get_activity(request.data)
        order_serializer = OrdersSerializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)

        payment_util = PaymentUtil(request,activity)
        charge = payment_util.pse_payu_payment()
        logger.error("ESTO ES EL URL DE PAGO --------------------\n")
        logger.error(charge)
        logger.error("ESTO ES EL URL DE PAGO ////////------------\n")
        return Response(status=200)


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
        logger.error(json.dumps(request.POST))

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

                
            pass

        elif transaction_status == settings.TRANSACTION_EXPIRED_CODE:
            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_declined_task(order,data)

        return Response(status=status.HTTP_200_OK)

