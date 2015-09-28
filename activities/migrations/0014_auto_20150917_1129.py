# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_auto_20150818_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activityphoto',
            name='activity',
            field=models.ForeignKey(to='activities.Activity', related_name='pictures'),
        ),
    ]
