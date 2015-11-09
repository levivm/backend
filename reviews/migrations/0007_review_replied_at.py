# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0006_auto_20151105_1244'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='replied_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
