from __future__ import absolute_import

from celery import Task, states
from django.conf import settings
from django.contrib.auth.models import User

from activities.models import Calendar, Activity, CalendarCeleryTaskEditActivity, \
    ActivityCeleryTaskEditActivity, ActivityStats
from utils.tasks import SendEmailTaskMixin


class CeleryTaskEditActivityMixin(SendEmailTaskMixin):
    CELERY_TASK_MODEL = None
    celery_task = None

    def register_task(self):
        self.celery_task = self.CELERY_TASK_MODEL.objects.create(
            task_id=self.request.id,
            state=states.PENDING,
            activity=self.activity)

    def get_merge_vars(self):
        return [{
                    'rcpt': assistant.email,
                    'vars': [{
                        'name': 'name',
                        'content': assistant.first_name,
                    }]
                } for assistant in self.assistants]

    def on_success(self, retval, task_id, args, kwargs):
        if self.celery_task is not None:
            self.celery_task.delete()
        return super(CeleryTaskEditActivityMixin, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        if self.celery_task is not None:
            self.celery_task.state = states.FAILURE
            self.celery_task.save(update_fields=['state'])
        return super(CeleryTaskEditActivityMixin, self).on_failure(exc, task_id, args, kwargs,
                                                                   einfo)


class SendEmailCalendarTask(CeleryTaskEditActivityMixin):
    CELERY_TASK_MODEL = CalendarCeleryTaskEditActivity

    def run(self, calendar_id, *args, **kwargs):
        self.calendar = Calendar.objects.get(id=calendar_id)
        if not self.calendar.tasks.filter(state=states.PENDING).exists():
            self.register_task()
            self.template_name = 'activities/email/change_calendar_data.html'
            self.emails = self.get_emails_to()
            self.subject = 'Una actividad ha cambiado'
            self.global_context = self.get_context_data()
            self.recipient_context = self.get_recipient_data()
            return super(SendEmailCalendarTask, self).run(*args, **kwargs)

    def register_task(self):
        self.celery_task = CalendarCeleryTaskEditActivity.objects.create(
            task_id=self.request.id,
            state=states.PENDING,
            calendar=self.calendar)

    def get_emails_to(self):
        self.assistants = [assistant for order in self.calendar.orders.available() for assistant in
                           order.assistants.enrolled()]
        emails = [assistant.email for assistant in self.assistants]
        return emails

    def get_context_data(self):
        return {
            'organizer': self.calendar.activity.organizer.name,
            'activity': self.calendar.activity.title,
            'closing_sales_date': self.calendar.closing_sale,
            'sessions': [{
                             'date': session.date,
                             'start_time': session.start_time,
                             'end_time': session.end_time,
                         } for session in self.calendar.sessions.all()],
            'price': self.calendar.session_price,
            'url_activity_id': '%sactivities/%s' % (settings.FRONT_SERVER_URL,
                                                    self.calendar.activity_id)
        }

    def get_recipient_data(self):
        return {a.email: {'name': a.first_name} for a in self.assistants}


class SendEmailLocationTask(CeleryTaskEditActivityMixin):
    CELERY_TASK_MODEL = ActivityCeleryTaskEditActivity

    def run(self, activity_id, *args, **kwargs):
        self.activity = Activity.objects.get(id=activity_id)
        if not self.activity.tasks.filter(state=states.PENDING).exists():
            self.register_task()
            self.template_name = 'activities/email/change_location_data.html'
            self.emails = self.get_emails_to()
            self.subject = 'Una actividad ha cambiado'
            self.global_context = self.get_context_data()
            self.recipient_context = self.get_recipient_data()
            return super(SendEmailLocationTask, self).run(*args, **kwargs)

    def get_emails_to(self):
        self.assistants = [assistant for calendar in self.activity.calendars.all()
                           for order in calendar.orders.available()
                           for assistant in order.assistants.enrolled()]
        emails = [assistant.email for assistant in self.assistants]
        return emails

    def get_context_data(self):
        return {
            'organizer': self.activity.organizer.name,
            'activity': self.activity.title,
            'address': self.activity.location.address,
            'detail_url': self.activity.get_frontend_url(),
        }

    def get_recipient_data(self):
        return {
            a.email: {
                'name': a.first_name,
            }
            for a in self.assistants
        }


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


class SendEmailShareActivityTask(SendEmailTaskMixin):
    def run(self, activity_id, user_id=None, user_name=None, *args, **kwargs):
        if user_id:
            self.user = User.objects.get(id=user_id)
            self.user_name = self.user.first_name
        else:
            self.user_name = user_name

        self.activity = Activity.objects.get(id=activity_id)
        self.template_name = 'activities/email/share_activity.html'
        self.emails = kwargs.get('emails')
        self.message = kwargs.get('message')
        self.subject = '%s ha compartido contigo algo en Trulii' % self.user_name
        self.global_context = self.get_context_data()

        return super(SendEmailShareActivityTask, self).run(*args, **kwargs)

    def get_context_data(self):
        cover = self.activity.pictures.get(main_photo=True)

        try:
            organizer_city = self.activity.organizer.locations.all()[0].city.name
        except IndexError:
            organizer_city = None

        if self.activity.rating > 0:
            rating = self.activity.rating
        elif self.activity.organizer.rating > 0:
            rating = self.activity.organizer.rating
        else:
            rating = None

        return {
            'name': self.user_name,
            'activity': {
                'cover_url': cover.photo.url,
                'title': self.activity.title,
                'initial_date': self.activity.closest_calendar().initial_date,
            },
            'category': {
                'color': self.activity.sub_category.category.color,
                'name': self.activity.sub_category.category.name,
            },
            'message': self.message,
            'organizer': {
                'name': self.activity.organizer.name,
                'city': organizer_city,
            },
            'rating': rating,
            'duration': self.activity.closest_calendar().duration // 3600,
            'price': self.activity.closest_calendar().session_price,
            'url': '%sactivities/%s/' % (settings.FRONT_SERVER_URL, self.activity.id),
        }


class ActivityViewsCounterTask(Task):

    def run(self, activity_id, user_id, *args, **kwargs):
        activity = Activity.objects.get(id=activity_id)
        if user_id != activity.organizer.user_id:
            stats, _ = ActivityStats.objects.get_or_create(activity=activity)
            stats.views_counter += 1
            stats.save(update_fields=['views_counter'])
