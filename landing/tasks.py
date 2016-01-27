from utils.tasks import SendEmailTaskMixin


class SendContactFormEmailTask(SendEmailTaskMixin):

    def run(self, data, *args, **kwargs):
        self.template_name = "landing/email/contact_us_form_message.txt"
        self.emails = ['contact@trulii.com']
        self.subject = 'Subject contact form'
        self.context = data
        self.global_merge_vars = self.get_global_merge_vars()
        return super(SendContactFormEmailTask, self).run(*args, **kwargs)
