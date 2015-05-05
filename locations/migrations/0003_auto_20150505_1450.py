# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0002_location_organizer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='location',
            name='organizer',
            field=models.ForeignKey(related_name='locations', to='organizers.Organizer', null=True),
        ),
    ]
