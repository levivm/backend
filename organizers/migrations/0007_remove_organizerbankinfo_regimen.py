# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-15 22:37
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0006_auto_20160908_1649'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organizerbankinfo',
            name='regimen',
        ),
    ]