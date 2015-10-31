# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_order_coupon'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='refund',
            unique_together=set([('order', 'assistant')]),
        ),
    ]
