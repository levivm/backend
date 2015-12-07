# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_auto_20151016_1037'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]
