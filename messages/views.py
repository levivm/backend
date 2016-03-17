from celery import group
from rest_framework.generics import ListCreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated

from messages.models import OrganizerMessageStudentRelation, OrganizerMessage
from messages.permissions import IsOrganizerOrReadOnly, CanRetrieveOrganizerMessage
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
            return self.profile.organizermessage_set.all().order_by('-pk')
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


class DetailOrganizerMessageView(RetrieveAPIView):
    serializer_class = OrganizerMessageSerializer
    permission_classes = (IsAuthenticated, CanRetrieveOrganizerMessage)
    queryset = OrganizerMessage.objects.all()
