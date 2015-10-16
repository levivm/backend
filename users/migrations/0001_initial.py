# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrganizerConfirmation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(verbose_name='created', default=django.utils.timezone.now)),
                ('key', models.CharField(verbose_name='key', max_length=64, unique=True)),
                ('sent', models.DateTimeField(verbose_name='sent', null=True)),
                ('used', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='RequestSignup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
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
