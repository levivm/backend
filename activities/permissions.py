from django.shortcuts import get_object_or_404
from rest_framework import permissions
from .models import Activity


class IsActivityOwner(permissions.BasePermission):

    def has_permission(self, request, view):
        activity_pk = view.kwargs.get('activity_pk')
        activity = get_object_or_404(Activity, pk=activity_pk)

        return request.user.has_perm('activities.change_activity', activity)
