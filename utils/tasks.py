from __future__ import absolute_import

from allauth.account.adapter import get_adapter
from celery import Task
from .models import CeleryTask



class SendEmailTaskMixin(Task):
    abstract = True
    success_handler = True

    def run(self, instance, template, **kwargs):
        emails = self.get_emails_to(instance)

        if emails:
            for celery_task in instance.tasks.all():
                task = self.AsyncResult(celery_task.task_id)
                if task.state == 'PENDING':
                    break
            else:
                context = self.get_context_data(instance)
                for email in emails:
                    get_adapter().send_mail(
                        template,
                        email,
                        context,
                    )
                
                self.register_task(instance)

                return 'Task scheduled'

    def register_task(self, instance):
        CeleryTask.objects.create(task_id=self.request.id, content_object=instance)

    def get_context_data(self,instance):
        data = {}
        return data

    def get_emails_to(self, instance):
        return []

    def on_success(self, retval, task_id, args, kwargs):
        if self.success_handler:
            task = CeleryTask.objects.get(task_id=task_id)
            task.delete()