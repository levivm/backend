# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-19 16:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trulii_messages', '0004_auto_20160317_1645'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organizermessagestudentrelation',
            options={'permissions': (('update_message', 'Can update a message'),)},
        ),
    ]
