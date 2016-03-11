from django.utils.translation import ugettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from activities.models import Calendar
from messages.models import OrganizerMessageStudentRelation
from messages.permissions import IsOrganizerOrReadOnly
from messages.serializers import OrganizerMessageSerializer
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
        self.validate_calendar()
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

    def related_to_students(self, organizer_message):
        students = [o.student for o in self.calendar.orders.available()]

        objects = [OrganizerMessageStudentRelation(
            organizer_message=organizer_message,
            student=student
        ) for student in students]

        OrganizerMessageStudentRelation.objects.bulk_create(objects)

    def validate_calendar(self):
        try:
            self.calendar = Calendar.objects.get(
                id=self.request.data.get('calendar_id'),
                activity__organizer=self.request.user.organizer_profile)
        except Calendar.DoesNotExist:
            raise ValidationError({'calendar': _('El calendario es requerido')})
