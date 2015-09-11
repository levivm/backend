# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='activity',
            field=models.ForeignKey(to='activities.Activity', related_name='reviews'),
        ),
        migrations.AlterField(
            model_name='review',
            name='author',
            field=models.ForeignKey(to='students.Student', related_name='reviews'),
        ),
    ]
