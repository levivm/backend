# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20150928_2304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assistant',
            name='email',
            field=models.EmailField(blank=True, max_length=254),
        ),
    ]
