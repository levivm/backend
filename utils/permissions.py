from rest_framework import permissions
from organizers.models import Organizer
from students.models import Student
from activities import constants as activities_constants



class UnpublishedActivitiesOnlyForOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        has_permission = True
        status = request.query_params.get('status')
        if status == activities_constants.UNPUBLISHED:
            has_permission = request.user.get_profile() == view.get_object() \
                                    if not request.user.is_anonymous() \
                                    else False
        return has_permission     

class DjangoObjectPermissionsOrAnonReadOnly(permissions.DjangoObjectPermissions):
    authenticated_users_only = False


class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user.get_profile(), Organizer)


class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return isinstance(request.user.get_profile(), Student)
