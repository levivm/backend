# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-17 08:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0020_auto_20160916_1252'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='headline',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]