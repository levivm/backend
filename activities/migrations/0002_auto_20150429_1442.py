# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='activity',
            name='large_description',
        ),
        migrations.RemoveField(
            model_name='activity',
            name='type',
        ),
        migrations.AddField(
            model_name='activity',
            name='certification',
            field=models.NullBooleanField(default=False),
        ),
    ]
