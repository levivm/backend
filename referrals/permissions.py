from rest_framework.permissions import BasePermission
from students.models import Student


class IsStudent(BasePermission):
    def has_permission(self, request, view):
        try:
            request.user.student_profile
        except (Student.DoesNotExist, AttributeError):
            return False

        return True