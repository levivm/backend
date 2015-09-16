# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_city'),
        ('referrals', '0002_auto_20150916_1551'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='owners',
        ),
        migrations.AddField(
            model_name='coupon',
            name='redeems',
            field=models.ManyToManyField(through='referrals.Redeem', to='students.Student'),
        ),
        migrations.AlterField(
            model_name='redeem',
            name='used',
            field=models.BooleanField(default=False),
        ),
    ]
