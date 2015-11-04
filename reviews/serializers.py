# -*- coding: utf-8 -*-

from rest_framework import serializers
from students.serializer import StudentsSerializer
from .models import Review
from utils.mixins import AssignPermissionsMixin


class ReviewSerializer(AssignPermissionsMixin, serializers.ModelSerializer):
    author = StudentsSerializer(read_only=True)
    reported = serializers.BooleanField(read_only=True)
    permissions = ('reviews.report_review', 'reviews.reply_review')

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
        )

    def create(self, validated_data):
        validated_data.update({'author': self.context['request'].data['author']})
        instance = super(ReviewSerializer, self).create(validated_data)
        self.assign_permissions(user=instance.activity.organizer.user, instance=instance)
        return instance