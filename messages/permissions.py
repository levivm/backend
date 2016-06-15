from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from organizers.models import Organizer


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return isinstance(request.user.get_profile(), Organizer)


class CanRetrieveOrganizerMessage(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('trulii_messages.retrieve_message', obj)


class CanUpdateOrganizerMessageRelation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'PATCH':
            return request.user.has_perm('trulii_messages.update_message', obj)
        return True

class CanDeleteOrganizerMessageRelation(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.has_perm('trulii_messages.delete_message', obj)
        return True
