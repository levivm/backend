# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_order_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_free',
            field=models.BooleanField(default=True),
        ),
    ]
