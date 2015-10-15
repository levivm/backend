# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0008_auto_20150929_0045'),
    ]

    operations = [
        migrations.CreateModel(
            name='RefundAssistant',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response_at', models.DateTimeField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RefundOrder',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response_at', models.DateTimeField()),
                ('order', models.ForeignKey(to='orders.Order')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='assistant',
            name='enrolled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='refundassistant',
            name='assistant',
            field=models.ForeignKey(to='orders.Assistant'),
        ),
        migrations.AddField(
            model_name='refundassistant',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
