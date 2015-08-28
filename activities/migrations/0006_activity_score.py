# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0005_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='score',
            field=models.FloatField(default=0),
        ),
    ]
