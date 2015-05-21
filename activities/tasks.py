from __future__ import absolute_import
from allauth.account.adapter import get_adapter

from celery import Task

from activities.models import CeleryTask, Chronogram, Activity


class SendEmailChronogramTask(Task):
    def run(self, chronogram_id, **kwargs):
        chronogram = Chronogram.objects.get(id=chronogram_id)
        for celery_task in chronogram.tasks.all():
            task = self.AsyncResult(celery_task.task_id)
            if task.state == 'PENDING':
                break
        else:
            context = self.get_context_data()
            email_template = 'activities/email/change_chronogram_data'
            emails = self.get_emails_to(chronogram)

            for email in emails:
                get_adapter().send_mail(
                    email_template,
                    email,
                    context
                )
            self.register_task(chronogram=chronogram)
            return 'Task scheduled'

    def register_task(self, chronogram):
        CeleryTask.objects.create(task_id=self.request.id, content_object=chronogram)

    def get_context_data(self):
        data = {}
        return data

    def get_emails_to(self, chronogram):
        assistants = [order.assistants.all() for order in chronogram.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails


class SendEmailLocationTask(Task):
    def run(self, activity_id, **kwargs):
        activity = Activity.objects.get(id=activity_id)
        for celery_task in activity.tasks.all():
            task = self.AsyncResult(celery_task.task_id)
            if task.state == 'PENDING':
                break
        else:
            context = self.get_context_data()
            email_template = 'activities/email/change_location_data'
            emails = self.get_emails_to(activity)

            for email in emails:
                get_adapter().send_mail(
                    email_template,
                    email,
                    context
                )
            self.register_task(activity=activity)
            return 'Task scheduled'

    def register_task(self, activity):
        CeleryTask.objects.create(task_id=self.request.id, content_object=activity)

    def get_context_data(self):
        data = {}
        return data

    def get_emails_to(self, activity):
        assistants = [order.assistants.all() for chronogram in activity.chronograms.all() for order in chronogram.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails