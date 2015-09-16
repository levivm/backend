# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0006_student_city'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('code', models.CharField(unique=True, max_length='15')),
                ('amount', models.IntegerField()),
                ('coupon_type', models.CharField(choices=[('global', 'Global'), ('referral', 'Referral')], default='referral', max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='Redeem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('used', models.BooleanField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('coupon', models.ForeignKey(to='referrals.Coupon')),
                ('student', models.ForeignKey(to='students.Student')),
            ],
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('ip_address', models.GenericIPAddressField()),
                ('referred', models.ForeignKey(to='students.Student', related_name='referreds')),
                ('referrer', models.ForeignKey(to='students.Student', related_name='referrers')),
            ],
        ),
        migrations.AddField(
            model_name='coupon',
            name='owners',
            field=models.ManyToManyField(through='referrals.Redeem', to='students.Student'),
        ),
    ]
