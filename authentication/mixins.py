from django.contrib.auth.models import Group
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from guardian.shortcuts import assign_perm
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


class SignUpMixin(object):
    """
    Mixin for the common SignUp methods
    """
    permissions = []
    profile_serializer = None
    group_name = None

    def create_token(self, user):
        return Token.objects.create(user=user)

    def get_profile_data(self, profile):
        serializer = self.profile_serializer(profile)
        return serializer.data

    def assign_group(self, user):
        group = Group.objects.get(name=self.group_name)
        user.groups.add(group)

    def assign_permissions(self, user, profile):
        for permission in self.permissions:
            assign_perm(permission, user, profile)


class ValidateTokenMixin(object):
    """
    Mixin to validate the auth token
    """

    model = None

    def validate_token(self, token):
        try:
            return self.model.objects.get(
                token=token,
                valid_until__gt=now(),
                used=False)
        except self.model.DoesNotExist:
            raise ValidationError(_('This token is not valid.'))


class InvalidateTokenMixin(object):
    model = None

    def invalidate_token(self, user):
        try:
            token_obj = self.model.objects.get(
                user=user,
                valid_until__gt=now(),
                used=False)
            token_obj.delete()
        except self.model.DoesNotExist:
            pass
