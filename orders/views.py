from django.contrib import messages
from django.http import Http404
from django.views.generic.base import TemplateView
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response

from activities.models import Activity
from orders.models import Assistant
from referrals.models import Coupon
from users.mixins import UserTypeMixin
from utils.paginations import MediumResultsSetPagination
from .mixins import ProcessPaymentMixin
from .models import Order
from .searchs import OrderSearchEngine
from .serializers import OrdersSerializer


class OrdersViewSet(UserTypeMixin, ProcessPaymentMixin, viewsets.ModelViewSet):
    serializer_class = OrdersSerializer
    queryset = Order.objects.all()
    permission_classes = (IsAuthenticated, DjangoObjectPermissions)
    pagination_class = MediumResultsSetPagination

    @staticmethod
    def get_activity(**kwargs):
        return get_object_or_404(Activity, id=kwargs.get('activity_pk'))

    @staticmethod
    def get_coupon(code):
        return get_object_or_404(Coupon, token=code)

    def create(self, request, *args, **kwargs):
        calendar = self.get_calendar(request)
        if calendar.is_free:
            request.data.update({'is_free': True})
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
        params = {'remove_fields': ['calendar', 'assistants', 'payment', 'coupon',
                                    'quantity', 'activity_id']}
        search = OrderSearchEngine()
        filter_query = search.filter_query(request.query_params)
        orders = search.get_by_student(student, filter_query)
        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrdersSerializer(page, many=True, **params)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(orders, many=True, **params)
        return Response(serializer.data)

    def list_by_organizer(self, request, *args, **kwargs):
        organizer = self.get_organizer(user=request.user, exception=PermissionDenied)
        params = {'remove_fields': ['calendar', 'assistants', 'payment', 'coupon',
                                    'quantity', 'activity_id']}
        search = OrderSearchEngine()
        filter_query = search.filter_query(request.query_params)
        orders = search.get_by_organizer(organizer, filter_query)

        page = self.paginate_queryset(orders)
        if page is not None:
            serializer = OrdersSerializer(page, many=True, **params)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(orders, many=True, **params)
        return Response(serializer.data)


class RefundAdminTemplateView(TemplateView):
    template_name = 'orders/refund_admin_view.html'

    def get_context_data(self, **kwargs):
        context = super(RefundAdminTemplateView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q:
            order = get_object_or_404(Order, id=q)
            assistants = order.assistants.all()
            context = {
                **context,
                'order': order,
                'assistants': assistants,
            }
        return context

    def post(self, request, *args, **kwargs):
        order_id = request.POST.get('order_id')
        assistant_id = request.POST.getlist('assistant_id')
        if order_id:
            self.cancel_order(order_id=order_id)
        elif assistant_id:
            self.cancel_assistants(assistant_id=assistant_id)
        context = self.get_context_data()
        return self.render_to_response(context)

    def cancel_order(self, order_id):
        order = Order.objects.get(id=order_id)
        order.change_status(Order.ORDER_CANCELLED_STATUS)
        order.assistants.all().update(enrolled=False)
        messages.success(self.request, 'Se canceló correctamente la order #{id}'.format(id=order_id))

    def cancel_assistants(self, assistant_id):
        assistants = Assistant.objects.filter(id__in=assistant_id)
        assistants.update(enrolled=False)
        assistant = assistants[0]
        if assistant.order.assistants.enrolled().count() == 0:
            assistant.order.change_status(Order.ORDER_CANCELLED_STATUS)
        messages.success(self.request, 'Se cancelaron correctamente los asistentes #{ids}'.format(
            ids=','.join(assistant_id)))
