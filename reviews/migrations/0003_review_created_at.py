# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20151103_1204'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 4, 15, 35, 5, 789914, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
