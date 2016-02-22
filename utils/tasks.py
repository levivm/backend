from __future__ import absolute_import

from celery import Task

from utils.mixins import MandrillMixin
from .models import EmailTaskRecord


class SendEmailTaskMixin(MandrillMixin, Task):
    abstract = True
    email_records = None
    context = None

    def run(self, *args, **kwargs):
        assert (self.template_name and
                self.emails and
                self.subject and
                self.context), ('Cannot send email on task that does not set template_name, '
                                'emails, subject, context')

        self.email_records = self.create_email_record_task()
        return self.send_mail()

    def create_email_record_task(self):
        params = [{
            'to': email,
            'template_name': self.template_name,
            'subject': self.subject,
            'data': self.context,
            'task_id': self.request.id,
        } for email in self.emails]

        return [EmailTaskRecord.objects.create(**param) for param in params]

    def on_success(self, retval, task_id, args, kwargs):
        if self.email_records is not None:
            records_hash = {e.to: e for e in self.email_records}

            for result in retval:
                email_record = records_hash[result['email']]
                email_record.status = result['status']
                email_record.reject_reason = '' if not result['reject_reason'] else \
                    result['reject_reason']
                email_record.smtp_id = result['_id']
                email_record.save()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.email_records is not None:
            for email_record in self.email_records:
                email_record.status = 'error'
                email_record.reject_reason = exc
                email_record.save(update_fields=['status', 'reject_reason'])

    def get_global_merge_vars(self):
        return [{'name': k, 'content': v} for k, v in self.context.items()]
