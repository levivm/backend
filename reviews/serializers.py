# -*- coding: utf-8 -*-
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from rest_framework import serializers

from orders.models import Order
from students.serializer import StudentsSerializer
from utils.mixins import AssignPermissionsMixin
from .models import Review


class ReviewSerializer(AssignPermissionsMixin, serializers.ModelSerializer):
    author = StudentsSerializer(read_only=True)
    reported = serializers.BooleanField(read_only=True)
    permissions = ('reviews.report_review', 'reviews.reply_review', 'reviews.read_review')

    class Meta:
        model = Review
        fields = (
            'id',
            'rating',
            'comment',
            'reply',
            'activity',
            'author',
            'created_at',
            'reported',
            'read',
            'replied_at',
        )

    def validate_reply(self, reply):
        if self.instance and self.instance.reply:
            raise serializers.ValidationError(_('No se puede cambiar la respuesta'))

        return reply

    def validate(self, data):
        if not self.instance:
            author = self.context['request'].data['author']
            activity = data.get('activity')
            if not author.orders.filter(status=Order.ORDER_APPROVED_STATUS, calendar__activity=activity,
                                        calendar__initial_date__lt=now()).exists():
                raise serializers.ValidationError(_('La orden no cumple con los requerimientos para crear un review'))
        else:
            if not self.instance.reply and data.get('reply'):
                data['replied_at'] = now()

        return data

    def create(self, validated_data):
        validated_data.update({'author': self.context['request'].data['author']})
        instance = super(ReviewSerializer, self).create(validated_data)
        self.assign_permissions(user=instance.activity.organizer.user, instance=instance)
        return instance
