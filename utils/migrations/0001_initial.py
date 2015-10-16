# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import allauth.socialaccount.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='CeleryTask',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('task_id', models.CharField(max_length=40)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='EmailTaskRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('data', allauth.socialaccount.fields.JSONField()),
                ('to', models.EmailField(max_length=254)),
                ('template', models.CharField(max_length=300)),
                ('send', models.BooleanField(default=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('task_id', models.CharField(max_length=40)),
            ],
        ),
    ]
