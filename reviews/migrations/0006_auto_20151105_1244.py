# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_review_read'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='review',
            options={'permissions': (('report_review', 'Report review'), ('reply_review', 'Reply review'), ('read_review', 'Read review'))},
        ),
    ]
