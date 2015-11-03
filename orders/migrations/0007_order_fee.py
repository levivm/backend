# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_fee'),
        ('orders', '0006_auto_20151028_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='fee',
            field=models.ForeignKey(to='payments.Fee', null=True, blank=True),
        ),
    ]
