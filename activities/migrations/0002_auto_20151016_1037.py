# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0003_organizer_headline'),
        ('activities', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='location',
            field=models.ForeignKey(to='locations.Location', null=True),
        ),
        migrations.AddField(
            model_name='activity',
            name='organizer',
            field=models.ForeignKey(to='organizers.Organizer'),
        ),
        migrations.AddField(
            model_name='activity',
            name='sub_category',
            field=models.ForeignKey(to='activities.SubCategory'),
        ),
        migrations.AddField(
            model_name='activity',
            name='tags',
            field=models.ManyToManyField(to='activities.Tags'),
        ),
    ]
