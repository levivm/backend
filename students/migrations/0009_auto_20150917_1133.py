# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_auto_20150917_1133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='referrer_code',
            field=models.CharField(unique=True, max_length=20),
        ),
    ]
