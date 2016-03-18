# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-18 15:59
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('students', '0003_auto_20160304_0910'),
        ('referrals', '0001_initial'),
        ('activities', '0003_activity_last_date'),
        ('payments', '0002_payment_response'),
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
                ('status', models.CharField(choices=[('approved', 'Aprobada'), ('pending', 'Pendiente'), ('cancelled', 'Cancelada'), ('declined', 'Declinada')], default='pending', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_free', models.BooleanField(default=False)),
                ('calendar', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='orders', to='activities.Calendar')),
                ('coupon', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='referrals.Coupon')),
                ('fee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='payments.Fee')),
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
