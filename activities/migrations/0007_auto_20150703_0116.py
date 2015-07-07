# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0006_activity_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='celerytask',
            name='content_type',
        ),
        migrations.DeleteModel(
            name='CeleryTask',
        ),
    ]
