from __future__ import absolute_import

from allauth.account.adapter import get_adapter
from celery import Task

from activities.models import CeleryTask, Chronogram, Activity


class SendEmailTaskMixin(Task):
    abstract = True

    def run(self, instance, template, **kwargs):
        for celery_task in instance.tasks.all():
            task = self.AsyncResult(celery_task.task_id)
            if task.state == 'PENDING':
                break
        else:
            context = self.get_context_data()
            emails = self.get_emails_to(instance)

            for email in emails:
                get_adapter().send_mail(
                    template,
                    email,
                    context
                )
            self.register_task(instance)
            return 'Task scheduled'

    def register_task(self, instance):
        CeleryTask.objects.create(task_id=self.request.id, content_object=instance)

    def get_context_data(self):
        data = {}
        return data

    def get_emails_to(self, instance):
        return []


class SendEmailChronogramTask(SendEmailTaskMixin):

    def run(self, chronogram_id, **kwargs):
        chronogram = Chronogram.objects.get(id=chronogram_id)
        template = 'activities/email/change_chronogram_data'
        return super(SendEmailChronogramTask, self).run(instance=chronogram, template=template)

    def get_emails_to(self, chronogram):
        assistants = [order.assistants.all() for order in chronogram.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails


class SendEmailLocationTask(SendEmailTaskMixin):
    def run(self, activity_id, **kwargs):
        activity = Activity.objects.get(id=activity_id)
        template = 'activities/email/change_location_data'
        return super(SendEmailLocationTask, self).run(instance=activity, template=template)

    def get_emails_to(self, activity):
        assistants = [order.assistants.all() for chronogram in activity.chronograms.all() for order in chronogram.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails