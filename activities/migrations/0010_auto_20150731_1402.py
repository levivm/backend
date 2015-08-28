# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_auto_20150714_1159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='enroll_open',
        ),
        migrations.AddField(
            model_name='chronogram',
            name='enroll_open',
            field=models.NullBooleanField(default=True),
        ),
    ]
