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
            field=models.DateTimeField(verbose_name='created', default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='organizerconfirmation',
            name='key',
            field=models.CharField(verbose_name='key', max_length=64, unique=True),
        ),
        migrations.AlterField(
            model_name='organizerconfirmation',
            name='sent',
            field=models.DateTimeField(verbose_name='sent', null=True),
        ),
    ]
