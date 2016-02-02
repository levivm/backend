# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

from django.contrib.auth.models import User
from rest_framework import serializers

from .models import RequestSignup, OrganizerConfirmation


# from allauth.account.forms import LoginForm

# 

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


class RequestSignupsSerializers(serializers.ModelSerializer):
    class Meta:
        model = RequestSignup
        
    def create(self, validated_data):
        validated_data['approved'] = False
        return super(RequestSignupsSerializers, self).create(validated_data)
