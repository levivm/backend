from celery import Task
# from utils.models import CeleryTask
from utils.tasks import SendEmailTaskMixin
# from allauth.account.utils import send_email_confirmation




class SendContactFormEmailTask(SendEmailTaskMixin):

    def run(self, instnace_id=None, success_handler=True, **kwargs):
        self.success_handler = True
        template = "landing/email/contact_us_form"
        return super(SendContactFormEmailTask, self).run(instance=None, template=template,**kwargs)

    def get_emails_to(self, data):
        emails = ['contact@trulii.com']
        return emails

    def get_context_data(self,data):

        return data