# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20150419_1949'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizerconfirmation',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
