import json

from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from django.utils.translation import ugettext_lazy as _

from orders.mixins import ProcessPaymentTaskMixin
from .models import Payment
from .tasks import SendPaymentEmailTask
from orders.models import Order
from activities.utils import PaymentUtil
from utils.loggers import PaymentLogger



class PayUBankList(APIView):
    def get(self, request, *args, **kwargs):
        payment_util = PaymentUtil(request)
        bank_list = payment_util.get_bank_list()
        return Response(bank_list)


class PayUNotificationPayment(APIView):
    PSE_METHOD_PAYMENT_ID = '4'
    CC_METHOD_PAYMENT_ID = '2'

    def _run_transaction_approved_task(self, order, data):
        order.change_status(Order.ORDER_APPROVED_STATUS)
        if order.coupon:
            order.coupon.set_used(student=order.student)
        task_data = {'payment_method': data.get('payment_method_type')}

        process_payment_task_mixin = ProcessPaymentTaskMixin(order=order,
                                                             task_data=task_data)
        process_payment_task_mixin.trigger_approved_tasks()

    def _run_transaction_declined_task(self, order, data, msg='Error',
                                       status=Order.ORDER_DECLINED_STATUS):
        order.change_status(status)
        error = data.get('response_message_pol')
        task_data = {
            'transaction_error': PaymentUtil.RESPONSE_CODE_NOTIFICATION_URL.get(error, msg),
            'payment_method': data.get('payment_method_type')
        }

        task = SendPaymentEmailTask()
        task.apply_async((order.id,), task_data, countdown=4)

    def _proccess_pse_payment_response(self, order, data):
        # state_pol response_code_pol
        #     4            1           Transacción aprobada
        #     6            5           Transacción fallida
        #     6            4           Transacción rechazada
        #     12          9994         Transacción pendiente, por favor revisar si el \
        #                                       débito fue realizado en el banco.

        transaction_status = data.get('state_pol')
        response_code_pol = data.get('response_code_pol')

        if transaction_status == settings.TRANSACTION_APPROVED_CODE:
            self.logger.log_payu_response('PSE Payment Response Successful', 
                                          order.student.user, data, self.request)
            self._run_transaction_approved_task(order, data)

        elif transaction_status == settings.TRANSACTION_DECLINED_CODE \
                and response_code_pol == settings.RESPONSE_CODE_POL_FAILED:

            self.logger.log_payu_response('PSE Payment Response failed', 
                                          order.student.user, data, self.request)

            _msg = _('Transacción Fallida')
            self._run_transaction_declined_task(order, data, _msg)

        elif transaction_status == settings.TRANSACTION_DECLINED_CODE \
                and response_code_pol == settings.RESPONSE_CODE_POL_DECLINED:

            self.logger.log_payu_response('PSE Payment Response declined', 
                                          order.student.user, data, self.request)

            _msg = _('Transacción Rechazada')
            self._run_transaction_declined_task(order, data, _msg)

        elif transaction_status == settings.TRANSACTION_PENDING_PSE_CODE:

            self.logger.log_payu_response('PSE Payment Response still pending', 
                                          order.student.user, data, self.request)


            _msg = 'Transacción pendiente, por favor revisar'
            _msg += 'si el débito fue realizado en el banco.'
            _msg = _(_msg)
            self._run_transaction_declined_task(order, data, _msg, Order.ORDER_PENDING_STATUS)

        return Response(status=status.HTTP_200_OK)

    def _proccess_cc_payment_response(self, order, data):

        transaction_status = data.get('state_pol')

        if transaction_status == settings.TRANSACTION_APPROVED_CODE:

            self.logger.log_payu_response('CC Payment Response Successful', 
                                          order.student.user, data, self.request)
            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_approved_task(order, data)

        elif transaction_status == settings.TRANSACTION_DECLINED_CODE:

            self.logger.log_payu_response('CC Payment Response declined', 
                                          order.student.user, data, self.request)

            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_declined_task(order, data)

            pass

        elif transaction_status == settings.TRANSACTION_EXPIRED_CODE:

            self.logger.log_payu_response('CC Payment Response expired', 
                                          order.student.user, data, self.request)
            if order.status == Order.ORDER_PENDING_STATUS:
                self._run_transaction_declined_task(order, data)

        return Response(status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):

        #Init the logger
        self.logger = PaymentLogger()

        # The responses code: http://developers.payulatam.com/es/web_checkout/variables.html
        data = request.data

        transaction_id = data.get('transaction_id')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            payment.response = json.dumps(request.POST)
            payment.save()
        except Payment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        order = payment.order

        payment_method = data.get('payment_method_type')

        if payment_method == settings.PSE_METHOD_PAYMENT_ID:
            return self._proccess_pse_payment_response(order, data)
        else:
            return self._proccess_cc_payment_response(order, data)
