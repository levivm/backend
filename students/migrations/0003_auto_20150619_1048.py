# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0002_auto_20150619_1040'),
    ]

    operations = [
        migrations.RenameField(
            model_name='student',
            old_name='birthdate',
            new_name='birth_date',
        ),
    ]