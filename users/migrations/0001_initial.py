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
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('user_type', models.CharField(max_length=1, choices=[('O', 'Organizador'), ('S', 'Estudiante')])),
                ('gender', models.PositiveIntegerField(default=1, choices=[(1, 'Hombre'), (0, 'Mujer')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.CharField(blank=True, null=True, max_length=100, verbose_name='Foto')),
                ('birthday', models.DateField(blank=True, null=True)),
                ('telephone', models.CharField(blank=True, null=True, max_length=100)),
                ('bio', models.TextField(blank=True, null=True)),
                ('user', models.OneToOneField(related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
