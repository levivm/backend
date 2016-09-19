# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-15 18:02
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20160915_1234'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fee_detail',
            field=django.contrib.postgres.fields.jsonb.JSONField(default={}),
            preserve_default=False,
        ),
    ]
