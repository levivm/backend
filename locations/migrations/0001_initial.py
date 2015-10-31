# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0003_organizer_headline'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('order', models.IntegerField(default=0)),
                ('point', models.CharField(max_length='200')),
            ],
            options={
                'verbose_name_plural': 'cities',
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('address', models.TextField()),
                ('point', models.CharField(max_length='200')),
                ('city', models.ForeignKey(to='locations.City')),
                ('organizer', models.ForeignKey(to='organizers.Organizer', null=True, related_name='locations')),
            ],
        ),
    ]
