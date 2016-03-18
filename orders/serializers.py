# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from rest_framework import serializers

from orders.models import Order, Assistant
from organizers.models import Organizer
from payments.models import Fee
from payments.serializers import PaymentSerializer
from referrals.tasks import ReferrerCouponTask
from students.models import Student
from students.serializer import StudentsSerializer
from utils.serializers import UnixEpochDateField, RemovableSerializerFieldMixin


class AssistantTokenField(serializers.SerializerMethodField):
    """
    Show assistant token if the current user is the order owner
    """

    def to_internal_value(self, data):
        pass

    def to_representation(self, obj):
        request = self.context.get('request')
        show_token = self.context.get('show_token')
        if show_token:
            return obj.token

        if request:
            current_user = request.user
            is_activity_owner = obj.order.calendar.activity.organizer.user == current_user
            is_order_owner = obj.order.student.user == current_user
            return obj.token if is_activity_owner or is_order_owner else None
        return None


class AssistantsSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    student = serializers.SerializerMethodField()
    token = AssistantTokenField(read_only=True)
    full_name = serializers.SerializerMethodField()
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    def get_full_name(self, obj):
        return "{} {}".format(obj.first_name, obj.last_name)

    class Meta:
        model = Assistant
        fields = (
            'id',
            'first_name',
            'last_name',
            'full_name',
            'email',
            'student',
            'order',
            'token'
        )

    def get_student(self, obj):
        student = Student.get_by_email(obj.email)
        student_serializer = StudentsSerializer(student)
        return student_serializer.data


class OrdersSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    assistants = AssistantsSerializer(many=True)
    student = StudentsSerializer(read_only=True)
    amount = serializers.FloatField(read_only=True)
    activity_id = serializers.SerializerMethodField()
    calendar_initial_date = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    created_at = UnixEpochDateField(read_only=True)
    payment = PaymentSerializer(read_only=True)
    fee = serializers.SerializerMethodField(read_only=True)
    coupon = serializers.SerializerMethodField()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = (
            'id',
            'calendar',
            'student',
            'quantity',
            'assistants',
            'amount',
            'status',
            'activity',
            'created_at',
            'payment',
            'calendar_initial_date',
            'activity_id',
            'fee',
            'is_free',
            'total',
            'total_without_coupon',
            'coupon',
        )

    def get_activity(self, obj):
        return {
            'id': obj.calendar.activity.id,
            'name': obj.calendar.activity.title
        }

    def get_activity_id(self, obj):
        return obj.calendar.activity.id

    def get_status(self, obj):
        return obj.get_status_display()

    def get_calendar_initial_date(self, obj):
        initial_date = obj.calendar.initial_date
        return UnixEpochDateField().to_representation(initial_date)

    def get_fee(self, obj):
        if obj.fee:
            return obj.fee.amount
        return None

    def get_coupon(self, obj):
        if obj.coupon:
            return {
                'amount': obj.coupon.coupon_type.amount,
                'code': obj.coupon.token
            }
        return None

    def validate_amount(self, obj):
        return obj.calendar.session_price * obj.quantity

    def validate_quantity(self, quantity):
        assistants = self.initial_data['assistants']
        if isinstance(assistants, list):
            count_assistants = len(assistants)
        else:
            count_assistants = 1

        if quantity != count_assistants:
            raise serializers.ValidationError(_('La cantidad de cupos no coincide con la '
                                                'cantidad de asistentes'))

        return quantity

    def validate(self, data):

        calendar = data.get('calendar')
        assistants_data = data.get('assistants')
        activity = calendar.activity

        if not activity.published:
            msg = str(_("La actividad no se encuentra activa"))
            raise serializers.ValidationError({'generalError': msg})

        if not calendar.enroll_open:
            msg = str(_("Las inscripciones están cerradas para esta fecha de inicio"))
            raise serializers.ValidationError({'generalError': msg})

        if not calendar.available_capacity() or \
                        calendar.available_capacity() < len(assistants_data):
            msg = str(_("El cupo de asistentes está lleno"))
            raise serializers.ValidationError({'generalError': msg})

        assistant_serializer = AssistantsSerializer(data=assistants_data, many=True)
        assistant_serializer.is_valid(raise_exception=True)

        return data

    def create(self, validated_data):
        assistants_data = validated_data.pop('assistants')
        student = self.context.get('view').student
        validated_data.update({
            'student': student,
            'status': self.context.get('status'),
            'payment': self.context.get('payment'),
            'coupon': self.context.get('coupon'),
        })
        order = Order(**validated_data)
        calendar = order.calendar
        order.amount = calendar.session_price * order.quantity

        if not calendar.is_free:
            order.fee = Fee.objects.last()

        order.save()

        for assistant in assistants_data:
            instance = Assistant(order=order, **assistant)
            instance.save()

        task = ReferrerCouponTask()
        task.delay(student_id=student.id, order_id=order.id)
        return order
