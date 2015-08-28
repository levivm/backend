# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0002_emailtaskrecord'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailtaskrecord',
            name='task_id',
            field=models.CharField(max_length=40, default=1),
            preserve_default=False,
        ),
    ]
