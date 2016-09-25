# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-25 02:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('organizers', '0001_initial'),
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.FloatField(default=0)),
                ('unavailable', models.FloatField(default=0)),
                ('organizer', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='balance', to='organizers.Organizer')),
            ],
        ),
        migrations.CreateModel(
            name='BalanceLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('available', 'Disponible'), ('unavailable', 'No Disponible'), ('withdrawn', 'Retirado'), ('requested', 'Solicitado')], default='unavailable', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balance_logs', to='orders.Order')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='balance_logs', to='organizers.Organizer')),
            ],
        ),
        migrations.CreateModel(
            name='Withdrawal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('amount', models.FloatField(default=0)),
                ('status', models.CharField(choices=[('pending', 'Pendiente'), ('approved', 'Aprobado'), ('declined', 'Rechazado')], default='pending', max_length=10)),
                ('logs', models.ManyToManyField(related_name='withdraws', to='balances.BalanceLog')),
                ('organizer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='withdrawals', to='organizers.Organizer')),
            ],
        ),
    ]
