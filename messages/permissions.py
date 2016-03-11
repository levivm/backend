from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from organizers.models import Organizer


class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return isinstance(request.user.get_profile(), Organizer)