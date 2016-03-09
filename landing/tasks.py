from utils.tasks import SendEmailTaskMixin


class SendContactFormEmailTask(SendEmailTaskMixin):

    def run(self, data, *args, **kwargs):
        self.template_name = "landing/email/contact_us.html"
        self.emails = ['levi@trulii.com']
        self.subject = 'Nuevo mensaje de Contact'
        self.global_context = data
        return super(SendContactFormEmailTask, self).run(*args, **kwargs)
