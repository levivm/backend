# -*- coding: utf-8 -*-

from rest_framework import serializers
from students.serializer import StudentsSerializer
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    student = StudentsSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            'rating',
            'comment',
            'reply',
            'activity',
            'student',
        )

    def create(self, validated_data):
        validated_data.update({'author': self.context['request'].data['author']})
        return super(ReviewSerializer, self).create(validated_data)
