from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      os.environ.get('DJANGO_SETTINGS_FILE', 'trulii.settings.local'))

from django.conf import settings

app = Celery('trulii')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(CELERY_ACCEPT_CONTENT = ['pickle', 'json'])
app.conf.update(
    CELERYBEAT_SCHEDULE = {
        # Executes every Wednesday at 12:00 A.M
        'add-every-wednesday-noon': {
            'task': 'reviews.tasks.SendReminderReviewEmailTask',
            'schedule': crontab(hour=12, minute=00, day_of_week=3),
        },
    }
)
