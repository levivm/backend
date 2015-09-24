# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0009_auto_20150917_1133'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=20)),
                ('amount', models.IntegerField()),
                ('coupon_type', models.CharField(choices=[('global', 'Global'), ('referral', 'Referral')], default='referral', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Redeem',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('token', models.CharField(unique=True, max_length=20)),
                ('used', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_used', models.DateField(editable=False)),
                ('coupon', models.ForeignKey(to='referrals.Coupon')),
                ('student', models.ForeignKey(to='students.Student')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('ip_address', models.GenericIPAddressField()),
                ('referred', models.ForeignKey(to='students.Student', related_name='referreds')),
                ('referrer', models.ForeignKey(to='students.Student', related_name='referrers')),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='redeems',
            field=models.ManyToManyField(to='students.Student', through='referrals.Redeem'),
        ),
    ]
