# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-15 22:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0007_remove_organizerbankinfo_regimen'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizerbankinfo',
            name='regimen',
            field=models.PositiveIntegerField(choices=[(1, 'Común'), (2, 'Gran Contribuyente')], null=True),
        ),
    ]