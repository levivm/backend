# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0003_redeem_used'),
        ('orders', '0008_auto_20150929_0045'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='coupon',
            field=models.ForeignKey(null=True, to='referrals.Coupon'),
        ),
    ]
