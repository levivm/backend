# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0002_auto_20150417_1545'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='organizer',
            field=models.ForeignKey(to='organizers.Organizer', null=True),
        ),
    ]
