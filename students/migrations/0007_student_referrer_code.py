# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='referrer_code',
            field=models.CharField(unique=True, max_length=20, default=1234),
            preserve_default=False,
        ),
    ]
