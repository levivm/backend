from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from organizers.models import Organizer
from students.models import Student
from .models import Order
from .serializers import OrdersSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, )

    def create(self, request, *args, **kwargs):
        try:
            student = Student.objects.get(user=request.user)
        except Student.DoesNotExist:
            raise PermissionDenied

        self.student = student
        return super().create(request, *args, **kwargs)

    def list_by_activity(self, request, *args, **kwargs):
        activity_pk = kwargs.get('activity_pk')
        organizer = get_object_or_404(Organizer, user=request.user)

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
        student = get_object_or_404(Student, user=request.user)
        order_pk = kwargs.get('order_pk')

        try:
            order = Order.objects.get(pk=order_pk)
        except Order.DoesNotExist:
            raise Http404

        if order.student != student:
            raise PermissionDenied

        serializer = self.get_serializer(order)
        return Response(serializer.data)

    def list_by_student(self, request, *args, **kwargs):
        student = get_object_or_404(Student, user=request.user)
        orders = student.orders.all()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)
