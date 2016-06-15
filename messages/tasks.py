from django.conf import settings
from celery import Task


from activities.models import Calendar
from students.models import Student
from messages.models import OrganizerMessage
from utils.tasks import SendEmailTaskMixin
from .models import OrganizerMessageStudentRelation


class SendEmailMessageNotificationTask(SendEmailTaskMixin):
    def run(self, organizer_message_id, *args, **kwargs):
        self.organizer_message = OrganizerMessage.objects.get(id=organizer_message_id)
        self.template_name = 'messages/email/student_notification.html'
        self.emails = [s.user.email for s in self.organizer_message.students.all()]
        self.subject = self.organizer_message.subject
        self.global_context = self.get_context_data()
        self.recipient_context = self.get_recipient_data()
        return super(SendEmailMessageNotificationTask, self).run(*args, **kwargs)

    def get_context_data(self):
        base_url = settings.FRONT_SERVER_URL
        return {
            'organizer': self.organizer_message.organizer.name,
            'url': '{base}student/dashboard/messages/{id}'.format(
                base=base_url,
                id=self.organizer_message.id)
        }

    def get_recipient_data(self):
        return {
            s.user.email: {
                'name': s.user.first_name,
            }
            for s in self.organizer_message.students.all()
        }


class SendEmailOrganizerMessageAssistantsTask(SendEmailTaskMixin):
    def run(self, organizer_message_id, *args, **kwargs):
        self.organizer_message = OrganizerMessage.objects.get(id=organizer_message_id)
        self.calendar = self.organizer_message.calendar
        self.template_name = 'messages/email/assistant_message.html'
        self.emails = self.get_emails()
        self.subject = self.organizer_message.subject
        self.global_context = self.get_context_data()
        self.recipient_context = self.get_recipient_data()
        return super(SendEmailOrganizerMessageAssistantsTask, self).run(*args, **kwargs)

    def get_emails(self):
        self.assistants = [assistant for o in self.calendar.orders.available() for assistant in
                           o.assistants.enrolled()]
        return [a.email for a in self.assistants]

    def get_context_data(self):
        return {
            'organizer': self.organizer_message.organizer.name,
            'message': self.organizer_message.message,
        }

    def get_recipient_data(self):
        return {
            a.email: {
                'name': a.first_name
            }
            for a in self.assistants
        }


class AssociateStudentToMessagesTask(Task):

    def run(self, calendar_id, student_id, *args, **kwargs):

        student = Student.objects.get(id=student_id)
        calendar = Calendar.objects.get(id=calendar_id)
        messages = OrganizerMessage.objects.filter(calendar=calendar)
        if not messages:
            return
        
        student_messages = []
        for message in messages:
            student_message, created = OrganizerMessageStudentRelation.\
                objects.get_or_create(student=student,
                    organizer_message=message)
            if created:
                student_messages.append(student_message)
        return student_messages
        



