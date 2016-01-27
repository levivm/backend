import json

from django.utils.timezone import now

from utils.tasks import SendEmailTaskMixin


class SendEmailOrganizerConfirmationTask(SendEmailTaskMixin):

    def run(self, organizer_confirmation_id, *args, **kwargs):
        from .models import OrganizerConfirmation
        self.confirmation = OrganizerConfirmation.objects.get(id=organizer_confirmation_id)
        self.template_name = "account/email/request_signup_confirmation_message.txt"
        self.emails = [self.confirmation.requested_signup.email]
        self.subject = 'Crea tu cuenta y comienza a user Trulii'
        self.context = self.get_context_data()
        self.global_merge_vars = self.get_global_merge_vars()
        return super(SendEmailOrganizerConfirmationTask, self).run(*args, **kwargs)

    def get_context_data(self):
        return {
            'activate_url': self.confirmation.get_confirmation_url(),
            'organizer': self.confirmation.requested_signup.name
        }

    def on_success(self, retval, task_id, args, kwargs):
        self.confirmation.sent = now()
        self.confirmation.save(update_fields=['sent'])
        super(SendEmailOrganizerConfirmationTask, self).on_success(retval, task_id, args, kwargs)


class SendAllAuthEmailTask(SendEmailTaskMixin):
    success_handler = True

    def run(self, user_id, success_handler=True, **kwargs):
        self.success_handler = success_handler

        account_adapter = kwargs['account_adapter']
        template = kwargs['email_data']['template_prefix']
        email    = kwargs['email_data']['email']
        msg = account_adapter.render_mail(**kwargs['email_data'])
        msg.send()

        self.register_email_record_task(template,self.request.id,email,**kwargs)
        return 'Task scheduled'

    def get_context_data(self,data):
        data = data['email_data']['context']
        return json.dumps(data, default=lambda o: o.id)