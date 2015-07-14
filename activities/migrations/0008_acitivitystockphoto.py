# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0007_auto_20150703_0116'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcitivityStockPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('photo', models.ImageField(upload_to='activities_stock')),
                ('sub_category', models.ForeignKey(to='activities.SubCategory')),
            ],
        ),
    ]
