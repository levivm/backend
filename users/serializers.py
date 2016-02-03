# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers, exceptions

from .models import RequestSignup, OrganizerConfirmation


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class OrganizerConfirmationsSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrganizerConfirmation


class RequestSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestSignup
        
    def create(self, validated_data):
        validated_data['approved'] = False
        return super(RequestSignUpSerializer, self).create(validated_data)

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise exceptions.ValidationError(_('This email already exists.'))

        return data
