# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-13 21:26
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('balances', '0003_auto_20160913_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='balancelog',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2016, 9, 13, 21, 26, 59, 664741, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
