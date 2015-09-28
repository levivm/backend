from __future__ import absolute_import
from django.conf import settings
from allauth.account.adapter import get_adapter
from celery import Task
from .models import EmailTaskRecord
from django.db import transaction





class SendEmailTaskMixin(Task):
    abstract = True
    success_handler = True


    def run(self, instance, template, **kwargs):
        emails = self.get_emails_to(instance)
        if emails:
            context = self.get_context_data(kwargs)

            for email in emails:
                self.register_email_record_task(template,self.request.id,email,**kwargs)
                get_adapter().send_mail(
                    template,
                    email,
                    context,
                )

            return 'Task scheduled'

    def get_email_record_task_data(self,template,task_id,to_email,**kwargs):

        data = {
            'to':to_email,
            'template':template,
            'data': self.get_context_data(kwargs),
            'task_id':task_id,
        }


        return data


    def register_email_record_task(self,template,task_id,to_email,**kwargs):
        data = self.get_email_record_task_data(template,task_id,to_email,**kwargs)
        email_task_record = EmailTaskRecord(**data)
        email_task_record.save()

    def get_context_data(self,instance):
        data = {}
        return data

    def get_emails_to(self, *args, **kwargs):
        return []

    def on_success(self, retval, task_id, args, kwargs):
        if self.success_handler:
            email_task_record = EmailTaskRecord.objects.get(task_id=task_id)
            email_task_record.send = True
            email_task_record.save()