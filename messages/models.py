from django.db import models

from activities.models import Calendar
from organizers.models import Organizer
from students.models import Student


class OrganizerMessage(models.Model):
    organizer = models.ForeignKey(Organizer)
    students = models.ManyToManyField(Student, related_name='organizer_messages',
                                     through='OrganizerMessageStudentRelation')
    calendar = models.ForeignKey(Calendar)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class OrganizerMessageStudentRelation(models.Model):
    organizer_message = models.ForeignKey(OrganizerMessage)
    student = models.ForeignKey(Student)
    read = models.BooleanField(default=False)
