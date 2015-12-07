# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0004_organizerbankinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='rating',
            field=models.FloatField(default=0),
        ),
    ]
