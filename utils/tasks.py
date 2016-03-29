from __future__ import absolute_import

import datetime

from celery import Task
from django.core.mail import send_mail
from django.template import loader, Context

from .models import EmailTaskRecord


class SendEmailTaskMixin(Task):
    abstract = True
    template_name = None
    emails = None
    subject = None
    email_records = None
    global_context = None
    recipient_context = {}

    def run(self, *args, **kwargs):
        assert (self.template_name and
                self.emails and
                self.subject and
                self.global_context is not None), ('Cannot send email on task that does not set template_name, '
                                'emails, subject, context')

        self.email_records = self.create_email_record_task()
        return self.send_mail()

    def create_email_record_task(self):

        params = [{
            'to': email,
            'template_name': self.template_name,
            'subject': self.subject,
            'data': {
                **self.sanitize_data(self.global_context),
                **self.sanitize_data(self.recipient_context.get(email, {})),
            },
            'task_id': self.request.id,
        } for email in self.emails]

        return [EmailTaskRecord.objects.create(**param) for param in params]

    def sanitize_data(self, data):
        new_data = data.copy()
        for key, value in new_data.items():
            if isinstance(value, (datetime.datetime, datetime.time)):
                new_data[key] = value.isoformat()
            elif isinstance(value, dict):
                new_data[key] = self.sanitize_data(value)
            elif isinstance(value, list):
                list_handler = lambda obj: (self.sanitize_data(obj) if isinstance(obj, dict)
                                            else obj)
                new_data[key] = [list_handler(item) for item in value]

        return new_data

    def on_success(self, retval, task_id, args, kwargs):
        if self.email_records is not None:
            records_hash = {e.to: e for e in self.email_records}

            for result in retval:
                email_record = records_hash[result['email']]
                email_record.status = result['status']
                email_record.reject_reason = '' if not result['reject_reason'] else \
                    result['reject_reason']
                email_record.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.email_records is not None:
            for email_record in self.email_records:
                email_record.status = 'error'
                email_record.reject_reason = exc
                email_record.save(update_fields=['status', 'reject_reason'])

    def send_mail(self):
        result = []
        template = loader.get_template(template_name=self.template_name)
        for email in self.emails:
            recipient_data = self.recipient_context.get(email, {})
            context_data = Context({**self.global_context, **recipient_data})
            html_message = template.render(context_data)

            try:
                result.append(send_mail(
                    subject=self.subject,
                    message='',
                    from_email='contacto@trulii.com',
                    recipient_list=[email],
                    html_message=html_message))
            except Exception:
                raise

        return result
