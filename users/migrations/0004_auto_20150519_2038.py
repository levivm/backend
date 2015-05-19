# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_organizerconfirmation_used'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizerconfirmation',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='created'),
        ),
        migrations.AlterField(
            model_name='organizerconfirmation',
            name='key',
            field=models.CharField(unique=True, max_length=64, verbose_name='key'),
        ),
        migrations.AlterField(
            model_name='organizerconfirmation',
            name='sent',
            field=models.DateTimeField(null=True, verbose_name='sent'),
        ),
    ]
