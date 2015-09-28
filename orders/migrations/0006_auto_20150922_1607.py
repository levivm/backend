# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20150818_1511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistant',
            name='token',
            field=models.CharField(unique=True, max_length=20),
        ),
    ]
