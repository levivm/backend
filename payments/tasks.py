from utils.tasks import SendEmailTaskMixin
from orders.models import Order
from django.conf import settings
from orders.serializers import OrdersSerializer,AssistantsSerializer
from .serializers import PaymentsSerializer
from activities.serializers import ChronogramsSerializer, ActivitiesSerializer

class SendPaymentEmailTask(SendEmailTaskMixin):

    def run(self, order_id, success_handler=True, **kwargs):
        self.success_handler = success_handler
        order  = Order.objects.get(id=order_id)
        import pdb
        pdb.set_trace()

        payment_method = kwargs.get('payment_method')
        if payment_method == settings.CC_METHOD_PAYMENT_ID:

            if order.status == Order.ORDER_APPROVED_STATUS:
                template = "payments/email/payment_approved_cc"
            elif order.status == Order.ORDER_DECLINED_STATUS:
                template = "payments/email/payment_declined_cc"
        elif payment_method == settings.PSE_METHOD_PAYMENT_ID:
            if order.status == Order.ORDER_APPROVED_STATUS:
                template = "payments/email/payment_approved_pse"
            elif order.status == Order.ORDER_DECLINED_STATUS:
                template = "payments/email/payment_declined_pse"
            elif order.status == Order.ORDER_PENDING_STATUS:
                template = "payments/email/payment_pending_pse"




        kwargs['order'] = order
        return super(SendPaymentEmailTask, self).run(instance=order, \
                        template=template,**kwargs)


    def get_emails_to(self, order):
        emails = [order.student.user.email]
        return emails

    def get_context_data(self,data):
        order   = data.get('order')
        assistants = order.assistants.all()
        assistants_data = AssistantsSerializer(assistants,many=True,\
                            context={'show_token':True}).data
        payment = order.payment
        chronogram = order.chronogram
        activity = chronogram.activity

        chronogram_data = ChronogramsSerializer(instance=chronogram).data
        activity_data = ActivitiesSerializer(instance=activity).data
        payment_data = PaymentsSerializer(instance=payment).data
        order_data = OrdersSerializer(instance=order).data

        context_data = {
            'order':order_data,
            'payment':payment_data,
            'chronogram':chronogram_data,
            'activity':activity_data,
            'assistants':assistants_data,
        }

        if not order.status == Order.ORDER_APPROVED_STATUS:
            context_data.update({'error':str(data.get('transaction_error'))})

        return context_data


    def on_success(self, retval, task_id, args,kwargs):
        super(SendPaymentEmailTask, self).on_success(retval, \
                            task_id,args,kwargs)
        order_id = args[0]
        order = Order.objects.get(id=order_id)

        if not order.status == Order.ORDER_APPROVED_STATUS and not \
            order.status == Order.ORDER_PENDING_STATUS:
            order.delete()



# class SendPaymentDeclainedEmailTask(SendEmailTaskMixin):

#     def run(self, student_id, success_handler=True, **kwargs):
#         self.success_handler = success_handler
#         order  = Order.objects.get(id=order_id)
#         template = "payments/email/payment_declined_cc"
#         kwargs['order'] = order
#         return super(SendPaymentDeclainedEmailTask, self).run(instance=order, \
#                         template=template,**kwargs)


#     def get_emails_to(self, order):
#         emails = [order.student.user.email]
#         return emails
