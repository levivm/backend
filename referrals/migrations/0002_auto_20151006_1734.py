# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupontype',
            old_name='coupon_type',
            new_name='type',
        ),
    ]
