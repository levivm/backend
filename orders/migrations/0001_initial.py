# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-25 02:44
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('referrals', '0001_initial'),
        ('activities', '0001_initial'),
        ('payments', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('enrolled', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('package_quantity', models.PositiveIntegerField(blank=True, null=True)),
                ('package_type', models.PositiveIntegerField(blank=True, choices=[(1, 'Mes(es)'), (2, 'Clase(s)')], null=True)),
                ('status', models.CharField(choices=[('approved', 'Aprobada'), ('pending', 'Pendiente'), ('cancelled', 'Cancelada'), ('declined', 'Declinada')], default='pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('fee', models.FloatField(default=0)),
                ('is_free', models.BooleanField(default=False)),
                ('fee_detail', django.contrib.postgres.fields.jsonb.JSONField(default={})),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='activities.Calendar')),
                ('coupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='referrals.Coupon')),
                ('payment', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.Payment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='students.Student')),
            ],
        ),
        migrations.AddField(
            model_name='assistant',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assistants', to='orders.Order'),
        ),
    ]
