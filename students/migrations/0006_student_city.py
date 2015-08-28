# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('locations', '0003_auto_20150505_1450'),
        ('students', '0005_auto_20150627_2146'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='city',
            field=models.ForeignKey(to='locations.City', null=True),
        ),
    ]
