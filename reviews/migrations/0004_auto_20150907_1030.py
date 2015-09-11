# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_auto_20150902_1532'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'permissions': (('report_review', 'Report review'), ('reply_review', 'Reply review'))},
        ),
    ]
