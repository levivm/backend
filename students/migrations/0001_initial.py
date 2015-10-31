# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('gender', models.PositiveIntegerField(choices=[(2, 'Hombre'), (1, 'Mujer')], default=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(upload_to='avatars', null=True, blank=True)),
                ('birth_date', models.DateTimeField(null=True)),
                ('referrer_code', models.CharField(max_length=20, unique=True)),
                ('city', models.ForeignKey(to='locations.City', null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, related_name='student_profile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
