# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('rating', models.FloatField()),
                ('comment', models.CharField(max_length=480, blank=True)),
                ('reply', models.CharField(max_length=480, blank=True)),
                ('activity', models.ForeignKey(to='activities.Activity', related_name='reviews')),
                ('author', models.ForeignKey(to='students.Student', related_name='reviews')),
            ],
            options={
                'permissions': (('report_review', 'Report review'), ('reply_review', 'Reply review')),
            },
        ),
    ]
