# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from orders.models import Order, Assistant
from students.serializer import StudentsSerializer
from students.models import Student


class AssistantSerializer(serializers.ModelSerializer):
    # order = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.SerializerMethodField()

    class Meta:
        model = Assistant
        fields = (
            # 'order',
            'first_name',
            'last_name',
            'email',
            'student'
        )

    def get_student(self,obj):
        student = Student.get_by_email(obj.email)
        student_serializer = StudentsSerializer(student)
        return student_serializer.data


class OrdersSerializer(serializers.ModelSerializer):
    assistants = AssistantSerializer(many=True)
    student = StudentsSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'chronogram',
            'student',
            'amount',
            'quantity',
            'assistants',
            'enroll',
        )

    def validate(self, data):
        chronogram = data.get('chronogram')
        assistants_data = data.get('assistants')
        activity = chronogram.activity

        if not activity.published:
            msg = _("La actividad no se encuentra activa")
            raise serializers.ValidationError({'detail':msg})

        if not chronogram.available_capacity() or chronogram.available_capacity()<len(assistants_data):
            msg = _("El cupo de asistentes está lleno")
            raise serializers.ValidationError({'detail':msg})

        assistant_serializer = AssistantSerializer(data=assistants_data, many=True)
        assistant_serializer.is_valid(raise_exception=True)

        return data

    def create(self, validated_data):
        assistants_data = validated_data.pop('assistants')
        validated_data.update({
            'student': self.context['view'].student,
            'enroll': self.context.get('charge', False)
        })
        order = Order.objects.create(**validated_data)
        assistant_objects = [Assistant(order=order, **assistant) for assistant in assistants_data]
        Assistant.objects.bulk_create(assistant_objects)
        return order
