# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-28 22:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0002_auto_20160925_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='instructors',
            field=models.ManyToManyField(blank=True, related_name='activities', to='organizers.Instructor'),
        ),
    ]
