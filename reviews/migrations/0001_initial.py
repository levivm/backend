# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0013_auto_20150818_1511'),
        ('students', '0006_student_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('rating', models.FloatField()),
                ('comment', models.CharField(blank=True, max_length=480)),
                ('reply', models.CharField(blank=True, max_length=480)),
                ('activity', models.ForeignKey(to='activities.Activity')),
                ('author', models.ForeignKey(to='students.Student')),
            ],
        ),
    ]
