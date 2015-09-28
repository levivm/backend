# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0012_chronogram_is_weekend'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='activity',
        ),
        migrations.DeleteModel(
            name='Review',
        ),
    ]
