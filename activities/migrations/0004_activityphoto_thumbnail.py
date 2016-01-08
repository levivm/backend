# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_activity_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='activityphoto',
            name='thumbnail',
            field=models.ImageField(upload_to='activities', null=True, blank=True),
        ),
    ]
