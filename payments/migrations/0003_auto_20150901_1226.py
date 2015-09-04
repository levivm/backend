# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0002_payment_last_four_digits'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_type',
            field=models.CharField(max_length=10, choices=[('PSE', 'PSE'), ('CC', 'Crédito')]),
        ),
    ]
