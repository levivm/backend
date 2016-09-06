from django.utils.timezone import now
from rest_framework import status
from rest_framework.response import Response
from django.core.exceptions import ObjectDoesNotExist

import logging

from django.conf import settings
from celery import group

from payments.models import Payment
from payments.tasks import SendPaymentEmailTask, SendNewEnrollmentEmailTask
from messages.tasks import AssociateStudentToMessagesTask
from activities.models import Calendar
from referrals.models import Redeem
from balances.tasks import CalculateOrganizerBalanceTask
from balances.models import BalanceLog
from referrals.tasks import ReferrerCouponTask, CreateCouponTask, SendCouponEmailTask
from activities.utils import PaymentUtil
from utils.loggers import PaymentLogger

from .models import Order


class ProcessPaymentMixin(object):
    coupon = None
    logger = logging.getLogger('payment')

    def proccess_payment(self, request, activity, serializer):
        """ Proccess payments """
        payment_method = request.data.get('payment_method')
        payment = PaymentUtil(request, activity, self.coupon)

        if payment_method == Payment.CC_PAYMENT_TYPE:

            response = self.proccess_payment_cc(payment, serializer)
            return response

        elif payment_method == Payment.PSE_PAYMENT_TYPE:
            response = self.proccess_payment_pse(payment, serializer)
            return response
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def get_calendar(request):
        calendar_id = request.data.get('calendar')
        calendar = Calendar.objects.get(id=calendar_id)
        return calendar

    @classmethod
    def get_organizer(cls, request):
        calendar = cls.get_calendar(request)
        return calendar.activity.organizer



    def call_create(self, serializer):
        super(ProcessPaymentMixin, self).perform_create(serializer)
        headers = super(ProcessPaymentMixin, self).get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def free_enrollment(self, serializer):
        logger = PaymentLogger()

        serializer.context['status'] = Order.ORDER_APPROVED_STATUS

        # New enrollment task 
        new_enrollment_task = SendNewEnrollmentEmailTask()

        # Create task to asociate student with calendar sent messages
        student_messages_task = AssociateStudentToMessagesTask()
        calendar_id = self.request.data.get('calendar')
        student_id = self.request.user.get_profile().id

        # Create order
        response = self.call_create(serializer)

        log_data = {
            'request': self.request,
            'order': serializer.data
        }
        logger.log_transaction('Free enrollment', log_data)

        # Asociate activities sent messages to the new student
        group(
            student_messages_task.s(calendar_id, student_id), 
            new_enrollment_task.s(response.data['id'])
        )()


        return response

    def proccess_payment_cc(self, payment, serializer):
        """ Process Credit Card Payments """

        logger = PaymentLogger()

        charge, raw_response, payu_request = payment.creditcard()

        if charge['status'] == 'APPROVED' or charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            serializer.context['coupon'] = self.coupon
            response = self.call_create(serializer=serializer)
            if charge['status'] == 'APPROVED':
                self.redeem_coupon(self.request.user.student_profile)
                task_data = {
                    'payment_method': settings.CC_METHOD_PAYMENT_ID
                }
                order = charge['payment'].order
                process_payment_task_mixin = ProcessPaymentTaskMixin(order=order,
                                                                     task_data=task_data)
                process_payment_task_mixin.trigger_approved_tasks()
            
            #Loggin CC Payment Success
            log_data = {
                'pay_u_parsed_response': charge,
                'pay_u_raw_response': raw_response,
                'payment_data':response.data, 
                'request': self.request,
                'payu_request': payu_request
            }
            logger.log_transaction('CC Payment Success', log_data)

            return response
        else:
            error = {'generalError': [charge['error']]}

            #Loggin CC Payment Error
            log_data = {
                'payu_response': charge['error'], 
                'payu_raw_response': raw_response, 
                'request': self.request,
                'payu_request': payu_request
            }

            logger.log_transaction('CC Payment Error', log_data)

            return Response(error, status=status.HTTP_400_BAD_REQUEST)

    def proccess_payment_pse(self, payment, serializer):
        """ Proccess PSE Payments """
        logger = PaymentLogger()

        charge, raw_response, payu_request = payment.pse_payu_payment()

        if charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            serializer.context['coupon'] = self.coupon
            response = self.call_create(serializer=serializer)

            log_data = {
                'pay_u_parsed_response': charge,
                'pay_u_raw_response': raw_response,
                'payment_data': response.data, 
                'request': self.request,
                'payu_request': payu_request
            }
            logger.log_transaction('PSE Payment Pending', log_data)

            return Response({'bank_url': charge['bank_url']}, status=status.HTTP_201_CREATED)
        else:
            error = {'generalError': [charge['error']]}

            log_data = {
                'payu_response': charge['error'], 
                'payu_raw_response': raw_response, 
                'request': self.request,
                'payu_request': payu_request
            }
            logger.log_transaction('PSE Payment Error', log_data)


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


class ProcessPaymentTaskMixin(object):
    """
    Mixin to handle the tasks after a payment was processed
    """

    def __init__(self, order, task_data):
        super(ProcessPaymentTaskMixin, self).__init__()
        self.order = order
        self.task_data = task_data
        self.calendar = order.calendar
        self.student_id = order.student_id
        self.organizer = order.calendar.activity.organizer

    def trigger_approved_tasks(self):
        #  Create task to associate student with calendar sent messages
        associate_student_to_messages_task = AssociateStudentToMessagesTask()

        # Create Balance log to organizer
        BalanceLog.create(organizer=self.organizer, calendar=self.calendar)

        # Crete task to recalculate organizer unavailable amount
        calculate_organizer_balance_task = CalculateOrganizerBalanceTask()

        # Send email about the payment (invoice)
        send_payment_email_task = SendPaymentEmailTask()

        # Send email to the organizer about the activity enrolled
        send_new_enrollment_email_task = SendNewEnrollmentEmailTask()

        # Referral coupon task
        referral_coupon_task = ReferrerCouponTask()
        create_coupon_task = CreateCouponTask()
        send_coupon_email_task = SendCouponEmailTask()

        group(
            associate_student_to_messages_task.s(self.calendar.id, self.student_id),
            calculate_organizer_balance_task.s([self.organizer.id]),
            send_payment_email_task.s(self.order.id, self.task_data),
            send_new_enrollment_email_task.s(self.order.id, self.task_data),
            (
                referral_coupon_task.s(self.student_id, self.order.id) |
                create_coupon_task.s() |
                send_coupon_email_task.s()
            ),
        )()
