# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_auto_20150429_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityphoto',
            name='main_photo',
            field=models.BooleanField(default=False),
        ),
    ]
