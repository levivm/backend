# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.CharField(choices=[('debit', 'Débito'), ('credit', 'Crédito')], max_length=10)),
                ('card_type', models.CharField(choices=[('visa', 'VISA'), ('mastercard', 'Mastercard'), ('amex', 'American Express'), ('diners', 'Diners')], max_length=25)),
                ('transaction_id', models.CharField(max_length=150)),
            ],
        ),
    ]
