from __future__ import absolute_import

import os

from celery import Celery
from kombu.entity import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trulii.settings')

from django.conf import settings

app = Celery('trulii')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

