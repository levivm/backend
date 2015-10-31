from rest_framework import permissions
from organizers.models import Organizer
from students.models import Student


class DjangoObjectPermissionsOrAnonReadOnly(permissions.DjangoObjectPermissions):
    authenticated_users_only = False


class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user.get_profile(), Organizer)


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user.get_profile(), Student)
