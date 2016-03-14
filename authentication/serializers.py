from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from rest_framework import serializers, exceptions



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
            msg = _("Ya existe un usuario registrado con este correo electrónico.")
            raise exceptions.ValidationError(msg)

        return data

    def validate(self, data):
        first_name = data['first_name']
        last_name = data['last_name']

        username = '%s.%s' % (first_name.lower(), last_name.lower())
        counter = User.objects.filter(username=username).count()

        if counter > 0:
            username += '%s' % (counter + 1)
        data['username'] = username
        return data

class ChangeEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.ValidationError(_('Este correo no existe'))

class ChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField()
    password1 = serializers.CharField()
    password2 = serializers.CharField()

    def validate_password(self, password):
        user = self.context['user']
        if not user.check_password(password):
            raise serializers.ValidationError(_('The current password is incorrect.'))
        return password

    def validate(self, data):
        password1 = data['password1']
        password2 = data['password2']

        if password1 != password2:
            raise serializers.ValidationError(_("The new password doesn't match."))

        return data
