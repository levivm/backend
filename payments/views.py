from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Payment
from rest_framework import status
import json


# Create your views here.




class PayUNotificationPayment(APIView):

    def post(self, request, *args, **kwargs):
        # print("request",request.POST)
        print(json.dumps(request.POST))
        #The responses code: http://developers.payulatam.com/es/web_checkout/variables.html
        data   = request.POST
        transaction_status = data.get('state_pol')
        if   transaction_status == settings.TRANSACTION_APPROVED_CODE:
            transaction_id = data.get('transaction_id')
            # payment = Payment.objects.get(transaction_id=transaction_id)
            # order   = payment.order
            # order.confirm_enrollment()

            
        elif transaction_status == settings.TRANSACTION_DECLINED_CODE:
            pass

        elif transaction_status == settings.TRANSACTION_EXPIRED_CODE:
            pass
        else:
            pass

        return Response(status=status.HTTP_200_OK)

