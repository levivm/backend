from django.http import Http404
from rest_framework import viewsets
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from orders.serializers import RefundSerializer

from users.mixins import UserTypeMixin
from .models import Order
from .mixins import ProcessPaymentMixin
from activities.models import Activity
from .serializers import OrdersSerializer
from utils.paginations import SmallResultsSetPagination


class OrdersViewSet(UserTypeMixin, ProcessPaymentMixin, viewsets.ModelViewSet):
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)

    def get_activity(self, **kwargs):
        return get_object_or_404(Activity, id=kwargs.get('activity_pk'))

    def create(self, request, *args, **kwargs):
        self.student = self.get_student(user=request.user)
        serializer = self.get_serializer(data=request.data)
        activity = self.get_activity(**kwargs)
        serializer.is_valid(raise_exception=True)

        calendar = self.get_calendar(request)
        if calendar.is_free:
            return self.free_enrollment(serializer)

        return self.proccess_payment(request, activity, serializer)

    def list_by_activity(self, request, *args, **kwargs):
        activity_pk = kwargs.get('activity_pk')
        organizer = self.get_organizer(user=request.user, exception=PermissionDenied)

        try:
            activity = organizer.activity_set.filter(pk=activity_pk). \
                prefetch_related('calendars__orders')[0]
        except IndexError:
            raise Http404

        orders = activity.get_orders()

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        order_pk = kwargs.get('order_pk')
        student = self.get_student(user=request.user, exception=PermissionDenied)

        order = get_object_or_404(Order, pk=order_pk)

        if order.student != student:
            raise Http404

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def list_by_student(self, request, *args, **kwargs):
        student = self.get_student(user=request.user, exception=PermissionDenied)
        orders = student.orders.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def list_by_organizer(self, request, *args, **kwargs):
        organizer = self.get_organizer(user=request.user, exception=PermissionDenied)
        orders = Order.objects.filter(calendar__activity__organizer=organizer)
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


class RefundCreateReadView(ListCreateAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return self.request.user.refunds.all()
