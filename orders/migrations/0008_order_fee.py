# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_fee'),
        ('orders', '0007_order_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fee',
            field=models.ForeignKey(to='payments.Fee', null=True, blank=True),
        ),
    ]
