# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_category_color'),
    ]

    operations = [
        migrations.AddField(
            model_name='chronogram',
            name='is_weekend',
            field=models.NullBooleanField(default=False),
        ),
    ]
