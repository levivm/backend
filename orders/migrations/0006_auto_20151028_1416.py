# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20151026_1448'),
    ]

    operations = [
        migrations.AlterField(
            model_name='refund',
            name='status',
            field=models.CharField(blank=True, max_length=10, choices=[('approved', 'Aprobado'), ('pending', 'Pendiente'), ('declined', 'Rechazado')], default='pending'),
        ),
    ]
