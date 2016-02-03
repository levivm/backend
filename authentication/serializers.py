from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers, exceptions

from organizers.models import Organizer


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if email and password:
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


class SignUpStudentSerializer(serializers.Serializer):
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    password1 = serializers.CharField()

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            msg = _("A user is already registered with this e-mail address.")
            raise exceptions.ValidationError(msg)

        return data

    def validate(self, data):
        first_name = data['first_name']
        last_name = data['last_name']

        data['username'] = '%s.%s' % (first_name.lower(), last_name.lower())
        return data
