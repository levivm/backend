# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0014_auto_20150917_1129'),
    ]

    operations = [
        migrations.AddField(
            model_name='chronogram',
            name='is_free',
            field=models.BooleanField(default=False),
        ),
    ]
