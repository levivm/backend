# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import allauth.socialaccount.fields


class Migration(migrations.Migration):

    dependencies = [
        ('utils', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailTaskRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', allauth.socialaccount.fields.JSONField()),
                ('to', models.EmailField(max_length=254)),
                ('template', models.CharField(max_length=300)),
                ('send', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
