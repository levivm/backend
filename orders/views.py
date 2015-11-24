from django.http import Http404
from rest_framework import viewsets
from rest_framework.generics import ListCreateAPIView, ListAPIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions, DjangoModelPermissions
from rest_framework.response import Response

from orders.models import Refund
from orders.serializers import RefundSerializer
from referrals.models import Coupon
from users.mixins import UserTypeMixin
from .models import Order
from .mixins import ProcessPaymentMixin
from activities.models import Activity
from .serializers import OrdersSerializer
from utils.paginations import SmallResultsSetPagination
from utils.permissions import IsOrganizer


class OrdersViewSet(UserTypeMixin, ProcessPaymentMixin, viewsets.ModelViewSet):
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)

    @staticmethod
    def get_activity(**kwargs):
        return get_object_or_404(Activity, id=kwargs.get('activity_pk'))

    @staticmethod
    def get_coupon(code):
        return get_object_or_404(Coupon, token=code)

    def create(self, request, *args, **kwargs):
        calendar = self.get_calendar(request)
        if calendar.is_free:
            request.data.update({'is_free':True})
        self.student = self.get_student(user=request.user)
        serializer = self.get_serializer(data=request.data)
        activity = self.get_activity(**kwargs)
        serializer.is_valid(raise_exception=True)

        if calendar.is_free:
            return self.free_enrollment(serializer)

        coupon_code = request.data.get('coupon_code')
        if coupon_code:
            self.coupon = self.get_coupon(code=request.data.get('coupon_code'))
            self.coupon.is_valid(request.user.student_profile)

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
        # serializer.context.update({'show_token':True})
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        order_pk = kwargs.get('order_pk')
        order = get_object_or_404(Order, pk=order_pk)

        try:
            student = self.get_student(user=request.user, exception=PermissionDenied)
            if order.student != student:
                raise Http404
        except PermissionDenied:
            organizer = self.get_organizer(user=request.user, exception=PermissionDenied) 
            if order.get_organizer() != organizer:
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
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return self.request.user.refunds.all()

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        return super(RefundCreateReadView, self).create(request, *args, **kwargs)


class RefundReadOrganizerView(ListAPIView):
    serializer_class = RefundSerializer
    permission_classes = [IsAuthenticated, IsOrganizer]
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        return Refund.objects.filter(order__calendar__activity__organizer=self.request.user.get_profile())
