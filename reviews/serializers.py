# -*- coding: utf-8 -*-
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from rest_framework import serializers

from orders.models import Order
from reviews.tasks import SendCommentToOrganizerEmailTask
from students.serializer import StudentsSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    author = StudentsSerializer(read_only=True)
    reported = serializers.BooleanField(read_only=True)
    activity_data = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = (
            'id',
            'rating',
            'comment',
            'reply',
            'activity',
            'activity_data',
            'author',
            'created_at',
            'reported',
            'read',
            'replied_at',
        )

    def get_activity_data(self, obj):
        return {
            'id': obj.activity.id,
            'title': obj.activity.title,
        }

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
        review = super(ReviewSerializer, self).create(validated_data)

        if validated_data.get('comment'):
            task = SendCommentToOrganizerEmailTask()
            task.delay(review_id=review.id)

        return review
