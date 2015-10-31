from __future__ import absolute_import

from allauth.account.adapter import get_adapter
from celery import Task

from activities.models import  Calendar, Activity
from utils.models import CeleryTask

class SendEmailActivityEditTaskMixin(Task):
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
                context = self.get_context_data()

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

    def on_success(self, retval, task_id, args, kwargs):
        if self.success_handler:
            task = CeleryTask.objects.get(task_id=task_id)
            task.delete()


class SendEmailCalendarTask(SendEmailActivityEditTaskMixin):

    def run(self, calendar_id, success_handler=True, **kwargs):
        self.success_handler = success_handler
        calendar = Calendar.objects.get(id=calendar_id)
        template = 'activities/email/change_calendar_data'
        return super(SendEmailCalendarTask, self).run(instance=calendar, template=template)

    def get_emails_to(self, calendar):
        assistants = [order.assistants.all() for order in calendar.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails


class SendEmailLocationTask(SendEmailActivityEditTaskMixin):
    def run(self, activity_id, success_handler=True, **kwargs):
        self.success_handler = success_handler
        activity = Activity.objects.get(id=activity_id)
        template = 'activities/email/change_location_data'
        return super(SendEmailLocationTask, self).run(instance=activity, template=template)

    def get_emails_to(self, activity):
        assistants = [order.assistants.all() for calendar in activity.calendars.all() for order in calendar.orders.all()]
        assistants = [item for sublist in assistants for item in sublist]
        emails = [assistant.email for assistant in assistants]
        return emails


class ActivityScoreTask(Task):

    def run(self, activity_id, *args, **kwargs):
        activity = Activity.objects.get(id=activity_id)
        details = self.get_detail_value(activity)
        gallery = self.get_gallery_value(activity)
        instructors = self.get_instructors_value(activity)
        return_policy = self.get_return_policy_value(activity)
        activity.score = details + gallery + instructors + return_policy
        activity.save(update_fields=['score'])

    def get_detail_value(self, activity):
        objective = 0.15 * bool(activity.goals)
        requirements = 0.2 * bool(activity.requirements)
        content = 0.4 * bool(activity.content)
        audience = 0.05 * bool(activity.audience)
        methodology = 0.1 * bool(activity.methodology)
        extra_info = 0.1 * bool(activity.extra_info)
        return 45 * (objective + requirements + content + audience + methodology + extra_info)

    def get_gallery_value(self, activity):
        video = 0.2 * bool(activity.youtube_video_url)
        gallery = (0.8 * activity.pictures.filter(main_photo=False).count()) / 5.0
        return 30 * (video + gallery)

    def get_instructors_value(self, activity):
        return 15 * bool(activity.instructors.count())

    def get_return_policy_value(self, activity):
        return 10 * bool(activity.return_policy)
