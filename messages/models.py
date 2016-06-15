from django.db import models

from activities.models import Calendar
from organizers.models import Organizer
from students.models import Student
from utils.mixins import AssignPermissionsMixin


class OrganizerMessage(AssignPermissionsMixin, models.Model):
    organizer = models.ForeignKey(Organizer)
    students = models.ManyToManyField(Student, related_name='organizer_messages',
                                     through='OrganizerMessageStudentRelation')
    calendar = models.ForeignKey(Calendar)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    permissions = ['trulii_messages.retrieve_message']

    class Meta:
        permissions = (
            ('retrieve_message', 'Can retrieve a message'),
            ('delete_message', 'Can delete a message'),
            ('update_message', 'Can update a message'),
        )

    def save(self, *args, **kwargs):
        super(OrganizerMessage, self).save(
            user=self.organizer.user,
            obj=self)


class OrganizerMessageStudentRelation(AssignPermissionsMixin, models.Model):
    organizer_message = models.ForeignKey(OrganizerMessage)
    student = models.ForeignKey(Student)
    read = models.BooleanField(default=False)

    permissions = ['trulii_messages.retrieve_message', 
                   'trulii_messages.delete_message',
                   'trulii_messages.update_message']

    def save(self, *args, **kwargs):
        super(OrganizerMessageStudentRelation, self).save(
            user=self.student.user,
            obj=self.organizer_message)
