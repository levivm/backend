from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from organizers.models import Organizer
from students.models import Student
from .models import Order
from .serializers import OrdersSerializer


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

    def create(self, request, *args, **kwargs):
        self.student = self._get_student(user=request.user)
        return super(OrdersViewSet,self).create(request, *args, **kwargs)

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
