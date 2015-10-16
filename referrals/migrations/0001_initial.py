# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('amount', models.IntegerField()),
                ('coupon_type', models.CharField(choices=[('global', 'Global'), ('referral', 'Referral')], max_length=15, default='referral')),
            ],
        ),
        migrations.CreateModel(
            name='Redeem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('token', models.CharField(max_length=20, unique=True)),
                ('used', models.BooleanField(default=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_used', models.DateField(editable=False, null=True)),
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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
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
