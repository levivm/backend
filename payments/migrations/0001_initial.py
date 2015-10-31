# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('payment_type', models.CharField(choices=[('PSE', 'PSE'), ('CC', 'Crédito')], max_length=10)),
                ('card_type', models.CharField(choices=[('visa', 'VISA'), ('mastercard', 'Mastercard'), ('amex', 'American Express'), ('diners', 'Diners')], max_length=25)),
                ('transaction_id', models.CharField(max_length=150)),
                ('last_four_digits', models.CharField(max_length=5)),
            ],
        ),
    ]
