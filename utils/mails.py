import sendgrid
from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.utils.timezone import now


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
            from_email=email_message.from_email,
        )

        for attachment in email_message.attachments:
            message.add_attachment_stream(attachment[0], attachment[1])

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


class ConsoleSendGridEmailBackend(SendGridEmailBackend):

    def send_messages(self, email_messages):
        email_message = email_messages[0]
        data = {
            'subject': email_message.subject,
            'from': email_message.from_email,
            'to': email_message.to,
            'date': now().isoformat(),
            'html': email_message.alternatives[0][0]
        }
        print("\n\
        \n==============================\
        \nSubject: {subject}\
        \nFrom: {from}\
        \nTo: {to}\
        \nDate: {date}\
        \n==============================\
        \n{html}".format(**data))

        return super(ConsoleSendGridEmailBackend, self).send_messages(email_messages)
