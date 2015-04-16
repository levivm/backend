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
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('gender', models.PositiveIntegerField(default=1, choices=[(1, 'Hombre'), (0, 'Mujer')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='avatars')),
                ('user', models.OneToOneField(related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
