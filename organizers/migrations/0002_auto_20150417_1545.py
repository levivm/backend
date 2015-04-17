# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='instructor',
            name='website',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='bio',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='instructor',
            name='organizer',
            field=models.ForeignKey(related_name='instructors', to='organizers.Organizer', null=True),
        ),
    ]
