# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0008_acitivitystockphoto'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AcitivityStockPhoto',
            new_name='ActivityStockPhoto',
        ),
    ]
