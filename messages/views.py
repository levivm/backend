from celery import group
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated

from messages.models import OrganizerMessageStudentRelation, OrganizerMessage
from messages.permissions import IsOrganizerOrReadOnly, CanRetrieveOrganizerMessage, \
    CanDeleteOrganizerMessageRelation
from messages.serializers import OrganizerMessageSerializer
from messages.tasks import SendEmailMessageNotificationTask, \
    SendEmailOrganizerMessageAssistantsTask
from organizers.models import Organizer
from utils.paginations import SmallResultsSetPagination


class ListAndCreateOrganizerMessageView(ListCreateAPIView):
    serializer_class = OrganizerMessageSerializer
    permission_classes = (IsAuthenticated, IsOrganizerOrReadOnly)
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        if isinstance(self.profile, Organizer):
            activity_id = self.request.GET.get('activity_id')
            if activity_id is None:
                raise ValidationError({'activity': 'La actividad es requerida.'})
            return self.profile.organizermessage_set.filter(
                calendar__activity__id=activity_id).order_by('-pk')
        else:
            return self.profile.organizer_messages.all().order_by('-pk')

    def create(self, request, *args, **kwargs):
        self.profile = request.user.get_profile()
        return super(ListAndCreateOrganizerMessageView, self).create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        self.profile = request.user.get_profile()
        return super(ListAndCreateOrganizerMessageView, self).list(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super(ListAndCreateOrganizerMessageView, self).get_serializer_context()

        if self.request.method == 'POST':
            context['organizer'] = self.profile
        return context

    def perform_create(self, serializer):
        organizer_message = serializer.save()
        self.related_to_students(organizer_message)
        notification_task = SendEmailMessageNotificationTask()
        send_email_task = SendEmailOrganizerMessageAssistantsTask()
        group(
            notification_task.s(organizer_message_id=organizer_message.id),
            send_email_task.s(organizer_message_id=organizer_message.id)
        )()

    def related_to_students(self, organizer_message):
        students = [o.student for o in organizer_message.calendar.orders.available()]

        for student in students:
            OrganizerMessageStudentRelation.objects.create(
                organizer_message=organizer_message,
                student=student)


class RetrieveDestroyOrganizerMessageView(RetrieveDestroyAPIView):
    serializer_class = OrganizerMessageSerializer
    permission_classes = (IsAuthenticated, CanRetrieveOrganizerMessage,
                          CanDeleteOrganizerMessageRelation)
    queryset = OrganizerMessage.objects.all()

    def perform_destroy(self, instance):
        try:
            relation = instance.organizermessagestudentrelation_set.get(
                student=self.request.user.student_profile)
        except OrganizerMessageStudentRelation.DoesNotExist:
            pass
        else:
            relation.delete()
