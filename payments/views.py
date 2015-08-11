from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Payment
from orders.models import ORDER_APPROVED_STATUS,ORDER_CANCELLED_STATUS,\
        ORDER_PENDING_STATUS
from rest_framework import status
import json


# Create your views here.




class PayUNotificationPayment(APIView):

    def post(self, request, *args, **kwargs):

        #The responses code: http://developers.payulatam.com/es/web_checkout/variables.html
        
        data   = request.POST
        transaction_status = data.get('state_pol')
        transaction_id = data.get('transaction_id')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        order   = payment.order

        if   transaction_status == settings.TRANSACTION_APPROVED_CODE:
            
            if order.status == ORDER_PENDING_STATUS:
                order.change_status(ORDER_APPROVED_STATUS)
                #send email
                #change order status

            
        elif transaction_status == settings.TRANSACTION_DECLINED_CODE:
            if order.status == ORDER_PENDING_STATUS:
                order.delete()
                #enviar correo de pago rechazado

                
            pass

        elif transaction_status == settings.TRANSACTION_EXPIRED_CODE:
            if order.status == ORDER_PENDING_STATUS:
                order.delete()
                #enviar correo que orden expiro

        return Response(status=status.HTTP_200_OK)

