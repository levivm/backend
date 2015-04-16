# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('amount', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('enroll', models.BooleanField(default=False)),
                ('chronogram', models.ForeignKey(related_name='orders', to='activities.Chronogram')),
                ('student', models.ForeignKey(to='students.Student')),
            ],
        ),
        migrations.AddField(
            model_name='assistant',
            name='order',
            field=models.ForeignKey(related_name='assistants', to='orders.Order'),
        ),
    ]
