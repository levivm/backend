from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.permissions import SAFE_METHODS

from .models import Activity


class IsActivityOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        activity_pk = view.kwargs.get('activity_pk')
        # TODO decidir si es activity_pk o pk. Manejar el caso cuando
        # no se necesite el activity_pk en la URL
        if not activity_pk:
            return True
        activity = get_object_or_404(Activity, pk=activity_pk)

        return request.user.has_perm('activities.change_activity', activity)


class IsActivityOwnerOrReadOnly(IsActivityOwner):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True

        return super().has_permission(request, view)