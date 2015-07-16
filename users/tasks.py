import json
from celery import Task
from utils.models import CeleryTask
from utils.tasks import SendEmailTaskMixin
# from allauth.account.utils import send_email_confirmation
from .models import OrganizerConfirmation
from students.models import Student
from organizers.models import Organizer




class SendEmailOrganizerConfirmationTask(SendEmailTaskMixin):

    def run(self, organizer_confirmation_id, success_handler=True, **kwargs):
        self.success_handler = success_handler
        confirmation  = OrganizerConfirmation.objects.get(id=organizer_confirmation_id)
        template = "account/email/request_signup_confirmation"
        return super(SendEmailOrganizerConfirmationTask, self).run(instance=confirmation, template=template,**kwargs)

    def get_emails_to(self, confirmation):
        emails = [confirmation.requested_signup.email]
        return emails

    def get_context_data(self,data):
        confirmation_id = data.get('confirmation_id')
        confirmation  = OrganizerConfirmation.objects.get(id=confirmation_id)

        if not confirmation.key:
            confirmation.key = confirmation.generate_key()
            confirmation.save()

        data = {
            'activate_url': confirmation.get_confirmation_url(),
            'organizer': confirmation.requested_signup.name

        }

        return data


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