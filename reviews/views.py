from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions
from rest_framework.response import Response
from activities.models import Activity
from .models import Review
from .serializers import ReviewSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (DjangoModelPermissions, )

    def get_student(self, request):
        try:
            return request.user.student_profile
        except:
            raise PermissionDenied

    def get_organizer(self, request):
        try:
            return request.user.organizer_profile
        except:
            raise PermissionDenied

    def create(self, request, *args, **kwargs):
        student = self.get_student(request)
        activity = self.get_activity(**kwargs)
        if self.allowed_to_create(student, activity):
            request.data.update({
                'activity': activity.id,
                'author': student,
            })
            return super(ReviewsViewSet, self).create(request, *args, **kwargs)

        raise PermissionDenied

    def allowed_to_create(self, student, activity):
        return student.orders.filter(chronogram__activity=activity).exists()

    def allowed_to_reply(self, organizer, activity):
        return organizer.activity_set.filter(id=activity.id).exists()

    def get_activity(self, **kwargs):
        activity = get_object_or_404(Activity, pk=kwargs.get('activity_pk'))
        return activity

    def reply(self, request, *args, **kwargs):
        organizer = self.get_organizer(request)
        review = self.get_object()
        activity = review.activity
        if self.allowed_to_reply(organizer, activity):
            review = self.get_object()
            review.reply = request.data.get('reply')
            review.save(update_fields=['reply'])
            return Response('OK')

        raise PermissionDenied
