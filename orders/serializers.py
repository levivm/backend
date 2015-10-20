# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers
from orders.models import Order, Assistant
from students.serializer import StudentsSerializer
from students.models import Student


class AssistantsSerializer(serializers.ModelSerializer):
    # order = serializers.PrimaryKeyRelatedField(read_only=True)
    student = serializers.SerializerMethodField()
    token   = serializers.SerializerMethodField()

    def get_token(self,obj):
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

    def get_student(self,obj):
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
            'chronogram',
            'student',
            'quantity',
            'assistants',
            'amount',
            'status',
        )


    def validate_amount(self,obj):
        return obj.chronogram.session_price*obj.quantity

    def validate(self, data):


        chronogram = data.get('chronogram')
        assistants_data = data.get('assistants')
        activity = chronogram.activity
        
        if not activity.published:
            msg = str(_("La actividad no se encuentra activa"))
            raise serializers.ValidationError({'generalError':msg})

        if not chronogram.enroll_open:
            msg = str(_("Las inscripciones están cerradas para esta fecha de inicio"))
            raise serializers.ValidationError({'generalError':msg})



        if not chronogram.available_capacity() or \
               chronogram.available_capacity()<len(assistants_data):
            msg = str(_("El cupo de asistentes está lleno"))
            raise serializers.ValidationError({'generalError':msg})

        assistant_serializer = AssistantsSerializer(data=assistants_data, many=True)
        assistant_serializer.is_valid(raise_exception=True)

        return data

    def create(self, validated_data):
        assistants_data = validated_data.pop('assistants')
        validated_data.update({
            'student': self.context.get('view').student,
            'status': self.context.get('status'),
            'payment': self.context.get('payment'),
        })
        order = Order(**validated_data)
        chronogram   = order.chronogram
        order.amount = chronogram.session_price * order.quantity
        order.save()

        for assistant in assistants_data:
            instance = Assistant(order=order, **assistant)
            instance.save()

        # assistant_objects = [Assistant(order=order, **assistant) for assistant in assistants_data]
        # Assistant.objects.bulk_create(assistant_objects)
        return order
