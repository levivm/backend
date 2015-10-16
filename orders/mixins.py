from rest_framework import viewsets,status
from payments.models import Payment
from rest_framework.response import Response
from payments.tasks import  SendPaymentEmailTask
from activities.models import Calendar
from .models import Order
from activities.utils import PaymentUtil
from django.conf import settings





class ProcessPaymentMixin(object):


    def proccess_payment(self, request, activity, serializer):
        """ Proccess payments """
        payment = PaymentUtil(request, activity)
        payment_method = request.data.get('payment_method')


        payment = PaymentUtil(request, activity)

        if payment_method == Payment.CC_PAYMENT_TYPE:
            return self.proccess_payment_cc(payment,serializer)
        elif payment_method == Payment.PSE_PAYMENT_TYPE:
            return self.proccess_payment_pse(payment,serializer)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_calendar(request):
        id = request.data.get('calendar')
        calendar = Calendar.objects.get(id=id)
        return calendar

    def call_create(self, serializer):
        super(ProcessPaymentMixin,self).perform_create(serializer)
        headers = super(ProcessPaymentMixin,self).get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def free_enrollment(self,serializer):
        serializer.context['status'] = Order.ORDER_APPROVED_STATUS
        return self.call_create(serializer)


    def proccess_payment_cc(self,payment,serializer):
        """ Proccess Credi Card Payments """

        charge = payment.creditcard()

        if charge['status'] == 'APPROVED' or charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            response = self.call_create(serializer=serializer)
            if charge['status'] == 'APPROVED':
                task = SendPaymentEmailTask()
                task_data = {
                   'payment_method':settings.CC_METHOD_PAYMENT_ID
                }
                task.apply_async((response.data['id'],),task_data, countdown=2)

            return response
        else:
            error = {'generalError':[charge['error']]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)


    def proccess_payment_pse(self,payment,serializer):
        """ Proccess PSE Payments """

        charge = payment.pse_payu_payment()        

        if charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            self.call_create(serializer=serializer)
            return Response({'bank_url':charge['bank_url']},status=status.HTTP_201_CREATED)
        else:
            error = {'generalError':[charge['error']]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
