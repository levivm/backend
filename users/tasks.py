
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

    def get_context_data(self,confirmation):

        confirmation.key = confirmation.generate_key()

        data = {
            'activate_url': confirmation.get_confirmation_url(),
            'organizer': confirmation.requested_signup.name

        }

        return data


class SendAllAuthEmailTask(Task):
    success_handler = True

    def run(self, user_id, success_handler=True, **kwargs):
        self.success_handler = success_handler
        try:
            instance = Student.objects.get(user=user_id)
        except Student.DoesNotExist:
            instance = Organizer.objects.get(user=user_id)

        for celery_task in instance.tasks.all():
            task = self.AsyncResult(celery_task.task_id)
            if task.state == 'PENDING':
                break
        else:
            account_adapter = kwargs['account_adapter']
            msg = account_adapter.render_mail(**kwargs['email_data'])
            msg.send()

            self.register_task(instance)
            return 'Task scheduled'

    def register_task(self, instance):
        CeleryTask.objects.create(task_id=self.request.id, content_object=instance)


    def on_success(self, retval, task_id, args, kwargs):
        if self.success_handler:
            task = CeleryTask.objects.get(task_id=task_id)
            task.delete()