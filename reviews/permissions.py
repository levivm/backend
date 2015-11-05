from rest_framework import permissions



class CanReadReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('reviews.read_review', obj)

class CanReportReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('reviews.report_review', obj)

class CanReplyReview(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.has_perm('reviews.reply_review', obj)