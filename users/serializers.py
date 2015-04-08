from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from allauth.account.forms import LoginForm

from rest_framework import exceptions, serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'last_name',
            'email',
        )


class UserProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'bio',
            'id',

        )


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

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

        attrs['user'] = user
        return attrs