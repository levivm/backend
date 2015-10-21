# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from orders.models import Order, Assistant, Refund
from referrals.tasks import ReferrerCouponTask
from students.serializer import StudentsSerializer
from students.models import Student


class AssistantsSerializer(serializers.ModelSerializer):
    # order = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.SerializerMethodField()
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        if self.context.get('show_token'):
            return obj.token

    class Meta:
        model = Assistant
        fields = (
            # 'order',
            'first_name',
            'last_name',
            'email',
            'student',
            'token'
        )

    def get_student(self, obj):
        student = Student.get_by_email(obj.email)
        student_serializer = StudentsSerializer(student)
        return student_serializer.data


class OrdersSerializer(serializers.ModelSerializer):
    assistants = AssistantsSerializer(many=True)
    student = StudentsSerializer(read_only=True)
    amount = serializers.FloatField(read_only=True)

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
        )

    def validate_amount(self, obj):
        return obj.calendar.session_price * obj.quantity

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
        order.save()
        assistant_objects = [Assistant(order=order, **assistant) for assistant in assistants_data]
        Assistant.objects.bulk_create(assistant_objects)
        task = ReferrerCouponTask()
        task.delay(student_id=student.id, order_id=order.id)
        return order


class RefundSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)

    class Meta:
        model = Refund
        fields = (
            'id',
            'order',
            'activity',
            'created_at',
            'amount',
            'status',
            'user',
            'assistant',
        )

    def get_activity(self, obj):
        return obj.order.calendar.activity.title

    def get_amount(self, obj):
        return obj.order.amount
