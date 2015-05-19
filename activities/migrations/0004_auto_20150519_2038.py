# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0003_activityphoto_main_photo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='short_description',
            field=models.CharField(max_length=300),
        ),
    ]
