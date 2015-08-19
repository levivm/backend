from django.http import Http404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets,status
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from activities.utils import PaymentUtil
from organizers.models import Organizer
from students.models import Student
from .models import Order
from activities.models import Activity
from .serializers import OrdersSerializer
from payments.tasks import  SendPaymentEmailTask



class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)

    def _get_student(self, user):
        try:
            return Student.objects.get(user=user)
        except Student.DoesNotExist:
            raise PermissionDenied

    def _get_organizer(self, user):
        try:
            return user.organizer_profile
        except Organizer.DoesNotExist:
            raise PermissionDenied

    def get_activity(self, **kwargs):
        return get_object_or_404(Activity, id=kwargs.get('activity_pk'))


    def _payment_cc(self,payment,serializer):
        charge = payment.creditcard()

        if charge['status'] == 'APPROVED' or charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            response = self.call_create(serializer=serializer)
            if charge['status'] == 'APPROVED':
                task = SendPaymentEmailTask()
                task.apply_async((response.data['id'],), countdown=4)
            return response
        else:
            return Response(charge['error'], status=status.HTTP_400_BAD_REQUEST)

        # return Response()

    def _payment_pse(self,payment,serializer):
        charge = payment.pse_payu_payment()

        if charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            self.call_create(serializer=serializer)
            # if charge['status'] == 'APPROVED':
            #     task = SendPaymentEmailTask()
            #     task.apply_async((response.data['id'],), countdown=4)
            return Response({'bank_url':charge['bank_url']})
        else:
            return Response(charge['error'], status=status.HTTP_400_BAD_REQUEST)


    def create(self, request, *args, **kwargs):
        self.student = self._get_student(user=request.user)
        serializer = self.get_serializer(data=request.data)
        activity = self.get_activity(**kwargs)
        serializer.is_valid(raise_exception=True)
        payment_method = request.data.get('payment_method')

        payment = PaymentUtil(request, activity)
        return getattr(self,'_payment_'+payment_method)(payment,serializer)


        charge = payment.creditcard()

        if charge['status'] == 'APPROVED' or charge['status'] == 'PENDING':

            serializer.context['status'] = charge['status'].lower()
            serializer.context['payment'] = charge['payment']
            response = self.call_create(serializer=serializer)
            if charge['status'] == 'APPROVED':
                task = SendPaymentEmailTask()
                task.apply_async((response.data['id'],), countdown=4)
            return response
        else:
            return Response(charge['error'], status=status.HTTP_400_BAD_REQUEST)

    def call_create(self, serializer):
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def list_by_activity(self, request, *args, **kwargs):
        activity_pk = kwargs.get('activity_pk')
        organizer = self._get_organizer(user=request.user)

        try:
            activity = organizer.activity_set.filter(pk=activity_pk).prefetch_related('chronograms__orders')[0]
        except IndexError:
            raise Http404

        chronograms = activity.chronograms.all()
        orders = [c.orders.all() for c in chronograms]
        orders = [order for sublist in orders for order in sublist]
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        order_pk = kwargs.get('order_pk')
        student = self._get_student(user=request.user)

        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            raise Http404

        if order.student != student:
            raise Http404

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def list_by_student(self, request, *args, **kwargs):
        student = self._get_student(user=request.user)
        orders = student.orders.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
