# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_auto_20150824_1044'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'permissions': (('report_review', 'Report review'),)},
        ),
    ]
