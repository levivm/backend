# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-08 21:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0005_organizerbankinfo_billing_telephone'),
    ]

    operations = [
        migrations.RenameField(
            model_name='organizerbankinfo',
            old_name='type_person',
            new_name='person_type',
        ),
    ]