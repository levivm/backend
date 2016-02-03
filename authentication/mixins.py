from django.contrib.auth.models import Group
from guardian.shortcuts import assign_perm
from rest_framework.authtoken.models import Token


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