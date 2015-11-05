# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_review_reported'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
