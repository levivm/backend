# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='birthdate',
            field=models.DateField(default=datetime.datetime(2015, 6, 19, 15, 40, 23, 284035, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='student',
            name='gender',
            field=models.PositiveIntegerField(choices=[(2, 'Hombre'), (1, 'Mujer')], default=2),
        ),
    ]
