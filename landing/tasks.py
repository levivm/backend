from utils.tasks import SendEmailTaskMixin


class SendContactFormEmailTask(SendEmailTaskMixin):

    def run(self, data, *args, **kwargs):
        self.template_name = "landing/email/contact_us.html"
        self.emails = ['contact@trulii.com']
        self.subject = 'Subject contact form'
        self.global_context = data
        return super(SendContactFormEmailTask, self).run(*args, **kwargs)
