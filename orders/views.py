from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from activities.models import Activity
from orders.serializers import OrdersSerializer


class OrdersViewSet(viewsets.ModelViewSet):
    serializer_class = OrdersSerializer

    def get_queryset(self):
        activity_id = self.kwargs.get('activity_pk', None)
        activity = get_object_or_404(Activity, pk=activity_id)
        return activity.order_set.all()
