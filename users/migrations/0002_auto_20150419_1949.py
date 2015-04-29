# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizerConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=django.utils.timezone.now, verbose_name=b'created')),
                ('key', models.CharField(unique=True, max_length=64, verbose_name=b'key')),
                ('sent', models.DateTimeField(null=True, verbose_name=b'sent')),
            ],
        ),
        migrations.CreateModel(
            name='RequestSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=100)),
                ('name', models.CharField(max_length=100)),
                ('telephone', models.CharField(max_length=100)),
                ('want_to_teach', models.TextField()),
                ('approved', models.BooleanField(default=False)),
                ('city', models.ForeignKey(to='locations.City')),
            ],
        ),
        migrations.AddField(
            model_name='organizerconfirmation',
            name='requested_signup',
            field=models.OneToOneField(to='users.RequestSignup'),
        ),
    ]
