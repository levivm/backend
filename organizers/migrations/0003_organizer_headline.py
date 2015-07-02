# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0002_auto_20150417_1545'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='headline',
            field=models.TextField(blank=True),
        ),
    ]
