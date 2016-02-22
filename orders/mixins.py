from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response

from django.conf import settings

from payments.models import Payment
from payments.tasks import SendPaymentEmailTask
from activities.models import Calendar
from referrals.models import Redeem
from .models import Order
from activities.utils import PaymentUtil
from django.core.exceptions import ObjectDoesNotExist


class ProcessPaymentMixin(object):
    coupon = None

    def proccess_payment(self, request, activity, serializer):
        """ Proccess payments """
        payment_method = request.data.get('payment_method')
        payment = PaymentUtil(request, activity, self.coupon)

        if payment_method == Payment.CC_PAYMENT_TYPE:
            return self.proccess_payment_cc(payment, serializer)
        elif payment_method == Payment.PSE_PAYMENT_TYPE:
            return self.proccess_payment_pse(payment, serializer)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_calendar(request):
        calendar_id = request.data.get('calendar')
        calendar = Calendar.objects.get(id=calendar_id)
        return calendar

    def call_create(self, serializer):
        super(ProcessPaymentMixin, self).perform_create(serializer)
        headers = super(ProcessPaymentMixin, self).get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def free_enrollment(self, serializer):
        serializer.context['status'] = Order.ORDER_APPROVED_STATUS
        return self.call_create(serializer)

    def proccess_payment_cc(self, payment, serializer):
        """ Process Credit Card Payments """
        charge = payment.creditcard()

        if charge['status'] == 'APPROVED' or charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            serializer.context['coupon'] = self.coupon
            response = self.call_create(serializer=serializer)
            if charge['status'] == 'APPROVED':
                self.redeem_coupon(self.request.user.student_profile)
                task = SendPaymentEmailTask()
                task_data = {
                    'payment_method': settings.CC_METHOD_PAYMENT_ID
                }
                task.apply_async((response.data['id'],), task_data, countdown=2)

            return response
        else:
            error = {'generalError': [charge['error']]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def proccess_payment_pse(self, payment, serializer):
        """ Proccess PSE Payments """

        charge = payment.pse_payu_payment()        

        if charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            serializer.context['coupon'] = self.coupon
            self.call_create(serializer=serializer)
            return Response({'bank_url': charge['bank_url']}, status=status.HTTP_201_CREATED)
        else:
            error = {'generalError': [charge['error']]}
            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def redeem_coupon(self, student):
        if self.coupon:
            try:
                redeem = self.coupon.redeem_set.get(student=student)
                redeem.set_used()
            except ObjectDoesNotExist:
                Redeem.objects.create(
                    student=student,
                    coupon=self.coupon,
                    used=True,
                    redeem_at=now()
                )
