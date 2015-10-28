# -*- coding: utf-8 -*-
from django.contrib.auth.models import User

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from rest_framework.fields import CreateOnlyDefault

from orders.models import Order, Assistant, Refund
from orders.tasks import SendEMailStudentRefundTask
from organizers.models import Organizer
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
            'id',
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

    def validate_quantity(self, quantity):
        assistants = self.initial_data['assistants']
        if isinstance(assistants, list):
            count_assistants = len(assistants)
        else:
            count_assistants = 1

        if quantity != count_assistants:
            raise serializers.ValidationError(_('La cantidad de cupos no coincide con la cantidad de asistentes'))

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
        order.save()

        for assistant in assistants_data:
            instance = Assistant(order=order, **assistant)
            instance.save()

        task = ReferrerCouponTask()
        task.delay(student_id=student.id, order_id=order.id)
        return order


class RefundSerializer(serializers.ModelSerializer):
    activity = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    assistant = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Assistant.objects.all(),
                                                   default=CreateOnlyDefault(None))

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

    def validate(self, data):
        order = data.get('order')
        assistant = data.get('assistant')
        user = data.get('user')

        if user:
            profile = user.get_profile()
            # Raise error if the order doesn't belong to the student
            if isinstance(profile, Student):
                if order.student != profile:
                    raise serializers.ValidationError(_('La orden no pertenece a este usuario.'))

            elif isinstance(profile, Organizer):
                if order.calendar.activity.organizer != profile:
                    raise serializers.ValidationError(_('La orden no pertenece a una actividad de este usuario.'))

        # Doesn't allow to create if the assistant doesn't belong to the order
        if assistant:
            if assistant.order != order:
                raise serializers.ValidationError(_('El asistente no pertenece a esa orden.'))

            if Refund.objects.filter(order=order, assistant__isnull=True).exists():
                raise serializers.ValidationError(_('No se puede crear un reembolso de orden '
                                                    'porque ya existe un reembolso de asistente '
                                                    'para esta misma orden'))

        else:
            if Refund.objects.filter(order=order, assistant__isnull=False).exists():
                raise serializers.ValidationError(_('No se puede crear un reembolso de asistente '
                                                    'porque ya existe un reembolso de orden '
                                                    'para esta misma orden'))

        return data

    def create(self, validated_data):
        validated_data['status'] = 'pending'
        instance = super(RefundSerializer, self).create(validated_data)
        task = SendEMailStudentRefundTask()
        task.delay(instance.id)
        return instance
