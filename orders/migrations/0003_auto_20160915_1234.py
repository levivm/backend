# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-15 17:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_order_package_quantity'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='fee',
            new_name='fee_2',
        ),
    ]
