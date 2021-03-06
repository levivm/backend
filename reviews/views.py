from django.http.response import JsonResponse, Http404
from django.views.generic.base import View
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied, NotAuthenticated
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import DjangoModelPermissions, \
    DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated
from rest_framework.response import Response

from activities.mixins import MongoMixin
from activities.models import Activity
from organizers.models import Organizer
from reviews.permissions import CanReportReview, CanReplyReview, CanReadReview
from reviews.tasks import SendReportReviewEmailTask, SendReplyToStudentEmailTask
from students.models import Student
from utils.paginations import PaginationBySize
from .models import Review
from .serializers import ReviewSerializer


class ReviewsViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (DjangoModelPermissions, CanReplyReview, CanReadReview)

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

    def get_activity(self, **kwargs):
        activity = get_object_or_404(Activity, pk=kwargs.get('activity_pk'))
        return activity

    def allowed_to_create(self, student, activity):
        return student.orders.filter(calendar__activity=activity).exists()

    def allowed_to_reply(self, organizer, activity):
        return organizer.activity_set.filter(id=activity.id).exists()

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

    def reply(self, request, *args, **kwargs):
        review = self.get_object()
        data = {'reply': request.data.get('reply'), 'read': True}
        serializer = self.get_serializer(review, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        task = SendReplyToStudentEmailTask()
        task.delay(review_id=review.id)
        return Response('OK')

    def read(self, request, *args, **kwargs):
        review = self.get_object()
        review.read = request.data.get('read', False)
        review.save(update_fields=['read'])
        return Response('OK')


class ReviewListByOrganizerViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    pagination_class = PaginationBySize
    permission_classes = (DjangoModelPermissionsOrAnonReadOnly,)

    def get_organizer(self, **kwargs):
        return get_object_or_404(Organizer, pk=kwargs.get('organizer_pk'))

    def list(self, request, *args, **kwargs):
        organizer = self.get_organizer(**kwargs)
        status = request.query_params.get('status')

        reviews = [activity.reviews.by_status(status).all() \
                   for activity in organizer.activity_set.filter(published=True)]
        reviews = [item for sublist in reviews for item in sublist]
        page = self.paginate_queryset(reviews)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ReviewListByStudentViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    pagination_class = PaginationBySize
    permission_classes = (IsAuthenticated, DjangoModelPermissions)

    def get_student(self, **kwargs):
        if not self.request.user.is_authenticated():
            raise NotAuthenticated()

        url_student = get_object_or_404(Student, pk=kwargs.get('student_pk'))

        try:
            user_student = self.request.user.student_profile
        except:
            raise PermissionDenied

        if url_student == user_student:
            return user_student

        raise PermissionDenied

    def list(self, request, *args, **kwargs):
        student = self.get_student(**kwargs)
        reviews = student.reviews.all()
        page = self.paginate_queryset(reviews)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class ReportReviewView(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    queryset = Review.objects.all()
    permission_classes = (IsAuthenticated, CanReportReview)

    def report(self, request, *args, **kwargs):
        review = self.get_object()
        review.reported = True
        review.read = True
        review.save(update_fields=['reported', 'read'])
        task = SendReportReviewEmailTask()
        task.delay(review.id)
        return Response()


class GhostReviewListView(MongoMixin, View):
    def get(self, *args, **kwargs):
        reviews = self.get_collection(name='reviews')
        activity_pk = int(kwargs['activity_pk'])
        try:
            activity = Activity.objects.get(id=activity_pk)
            data = []
            for review in reviews.find({'activity': activity_pk}, {'_id': False}):
                data.append({**review, 'activity_data': {
                    'id': activity.id,
                    'title': activity.title
                }})

            return JsonResponse(data, safe=False)
        except Activity.DoesNotExist:
            raise Http404
