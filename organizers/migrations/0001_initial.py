# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Instructor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('full_name', models.CharField(max_length=200)),
                ('bio', models.TextField()),
                ('photo', models.CharField(blank=True, null=True, max_length=1000, verbose_name='Foto')),
            ],
        ),
        migrations.CreateModel(
            name='Organizer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='avatars')),
                ('telephone', models.CharField(blank=True, max_length=100)),
                ('youtube_video_url', models.CharField(blank=True, max_length=100)),
                ('website', models.CharField(blank=True, max_length=100)),
                ('bio', models.TextField(blank=True)),
                ('user', models.OneToOneField(related_name='organizer_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='instructor',
            name='organizer',
            field=models.ForeignKey(related_name='instructors', to='organizers.Organizer'),
        ),
    ]
