# from django.shortcuts import get_object_or_404
from rest_framework import permissions
# from rest_framework.permissions import SAFE_METHODS

from .models import Organizer


class IsCurrentUserSameOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        organizer_pk = int(view.kwargs.get('organizer_pk'))
        # TODO decidir si es activity_pk o pk. Manejar el caso cuando
        # no se necesite el activity_pk en la URL
        if not organizer_pk:
            return True

        try:
        	if not request.user.organizer_profile.id == organizer_pk:
        		return False
        except Organizer.DoesNotExist:
        	return False

        return True