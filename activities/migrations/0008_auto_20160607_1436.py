# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-06-07 19:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0007_calendar_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='last_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]