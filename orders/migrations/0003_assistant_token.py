# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import orders.models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150428_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='assistant',
            name='token',
            field=models.CharField(default=orders.models.generate_token, max_length=5),
        ),
    ]
