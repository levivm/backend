# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
        ('orders', '0003_assistant_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='enroll',
        ),
        migrations.AddField(
            model_name='order',
            name='payment',
            field=models.OneToOneField(default=1, to='payments.Payment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(max_length=15, default='pending', choices=[('approved', 'Approved'), ('pending', 'Pending'), ('cancelled', 'Cancelled')]),
        ),
    ]
