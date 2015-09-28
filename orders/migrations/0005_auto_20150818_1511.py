# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150810_1044'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='pending', choices=[('approved', 'Aprobada'), ('pending', 'Pendiente'), ('cancelled', 'Cancelada'), ('declined', 'Declinada')], max_length=15),
        ),
    ]
