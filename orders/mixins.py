from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response

from django.conf import settings
from celery import group

from payments.models import Payment
from payments.tasks import SendPaymentEmailTask, SendNewEnrollmentEmailTask
from messages.tasks import AssociateStudentToMessagesTask
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

        # Create task to asociate student with calendar sent messages
        student_messages_task = AssociateStudentToMessagesTask()
        calendar_id = request.data.get('calendar')
        student_id = request.user.get_profile().id


        if payment_method == Payment.CC_PAYMENT_TYPE:

            response = self.proccess_payment_cc(payment, serializer)

            # Asociate activities sent messages to the new student
            student_messages_task.s(calendar_id, student_id)

            return response

        elif payment_method == Payment.PSE_PAYMENT_TYPE:
            response = self.proccess_payment_pse(payment, serializer)
            
            # Asociate activities sent messages to the new student
            student_messages_task.s(calendar_id, student_id)

            return response
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

        # New enrollment task 
        new_enrollment_task = SendNewEnrollmentEmailTask()

        # Create task to asociate student with calendar sent messages
        student_messages_task = AssociateStudentToMessagesTask()
        calendar_id = self.request.data.get('calendar')
        student_id = self.request.user.get_profile().id

        # Create order
        response = self.call_create(serializer)


        # Asociate activities sent messages to the new student
        group(
            student_messages_task.s(calendar_id, student_id), 
            new_enrollment_task.s(response.data['id'])
        )()


        return response

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
                payment_task = SendPaymentEmailTask()
                new_enrollment_task = SendNewEnrollmentEmailTask()

                task_data = {
                    'payment_method': settings.CC_METHOD_PAYMENT_ID
                }

                group(
                    payment_task.s(response.data['id'], task_data),
                    new_enrollment_task.s(response.data['id'], task_data)
                )()

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
