# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers, exceptions

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


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
            # login_form = LoginForm({'login':email,'password':password})
            # login_form.is_valid()

            # login_form.login(self.context['request']._request)
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise exceptions.ValidationError(msg)
            else:
                msg = _('Unable to log in with provided credentials.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)

        data['user'] = user
        return data
