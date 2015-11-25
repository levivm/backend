# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='requestsignup',
            name='want_to_teach',
        ),
        migrations.AddField(
            model_name='requestsignup',
            name='document',
            field=models.CharField(max_length=100, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='requestsignup',
            name='document_type',
            field=models.CharField(max_length=5, default='cc', choices=[('cc', 'C.C.'), ('nit', 'N.I.T.'), ('ce', 'C.E.')]),
            preserve_default=False,
        ),
    ]
