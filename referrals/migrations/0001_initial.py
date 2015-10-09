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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=20, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('valid_until', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CouponType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20, unique=True)),
                ('amount', models.IntegerField()),
                ('coupon_type', models.CharField(default='referral', choices=[('global', 'Global'), ('referral', 'Referral')], max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Redeem',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('redeem_at', models.DateTimeField(blank=True, null=True)),
                ('coupon', models.ForeignKey(to='referrals.Coupon')),
                ('student', models.ForeignKey(to='students.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('ip_address', models.GenericIPAddressField()),
                ('referred', models.ForeignKey(related_name='referreds', to='students.Student')),
                ('referrer', models.ForeignKey(related_name='referrers', to='students.Student')),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='coupon_type',
            field=models.ForeignKey(to='referrals.CouponType'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='redeems',
            field=models.ManyToManyField(through='referrals.Redeem', to='students.Student'),
        ),
    ]
