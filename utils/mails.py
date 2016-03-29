import sendgrid
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend


class SendGridEmailBackend(BaseEmailBackend):

    def __init__(self, fail_silently=False, **kwargs):
        super(SendGridEmailBackend, self).__init__(fail_silently=fail_silently, **kwargs)
        self.sg = sendgrid.SendGridClient(settings.SENDGRID_API_KEY, None, raise_errors=True)

    def send_messages(self, email_messages):
        email_message = email_messages[0]
        message = sendgrid.Mail(
                to=email_message.to,
                subject=email_message.subject,
                html=email_message.alternatives[0][0],
                from_email=email_message.from_email)
        try:
            status, msg = self.sg.send(message)
        except sendgrid.SendGridError:
            if not self.fail_silently:
                raise
        else:
            if status == 200:
                return {
                    'email': email_message.to[0],
                    'status': 'sent',
                    'reject_reason': None,
                }
