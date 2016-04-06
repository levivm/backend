# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-06 15:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0004_activity_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('views_counter', models.PositiveIntegerField(default=0)),
                ('activity', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='stats', to='activities.Activity')),
            ],
        ),
    ]
