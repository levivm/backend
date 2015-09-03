from rest_framework import permissions


class CanReportReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('reviews.report_review', obj)
