from django.utils.timezone import now

from utils.tasks import SendEmailTaskMixin


class SendEmailOrganizerConfirmationTask(SendEmailTaskMixin):

    def run(self, organizer_confirmation_id, *args, **kwargs):
        from .models import OrganizerConfirmation
        self.confirmation = OrganizerConfirmation.objects.get(id=organizer_confirmation_id)
        self.template_name = "authentication/email/request_signup_confirmation.html"
        self.emails = [self.confirmation.requested_signup.email]
        self.subject = 'Crea tu cuenta y comienza a user Trulii'
        self.global_context = self.get_context_data()
        return super(SendEmailOrganizerConfirmationTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'activate_url': self.confirmation.get_confirmation_url(),
        }

    def on_success(self, retval, task_id, args, kwargs):
        super(SendEmailOrganizerConfirmationTask, self).on_success(retval, task_id, args, kwargs)
        self.confirmation.sent = now()
        self.confirmation.save(update_fields=['sent'])
