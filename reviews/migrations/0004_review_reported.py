# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0003_review_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='reported',
            field=models.BooleanField(default=False),
        ),
    ]
