# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0009_order_is_free'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
    ]
