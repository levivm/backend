# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-12 15:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0011_subcategory_featured'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='sub_category',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='activities.SubCategory'),
        ),
    ]