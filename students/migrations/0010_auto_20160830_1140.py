# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-30 16:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_auto_20160810_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.PositiveIntegerField(choices=[(2, 'Hombre'), (1, 'Mujer')], null=True),
        ),
    ]