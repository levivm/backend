# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refundassistant',
            name='response_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='refundassistant',
            name='status',
            field=models.CharField(blank=True, max_length=10, choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')], default='pending'),
        ),
        migrations.AlterField(
            model_name='refundorder',
            name='response_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='refundorder',
            name='status',
            field=models.CharField(blank=True, max_length=10, choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')], default='pending'),
        ),
    ]
