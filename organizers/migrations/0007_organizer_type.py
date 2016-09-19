# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-13 20:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0006_auto_20160908_1649'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizer',
            name='type',
            field=models.CharField(choices=[('normal', 'Normal'), ('special', 'Especial')], default='normal', max_length=15),
        ),
    ]