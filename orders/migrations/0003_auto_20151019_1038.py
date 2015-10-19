# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0002_auto_20151016_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Refund',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, default='pending', max_length=10, choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response_at', models.DateTimeField(blank=True, null=True)),
                ('assistant', models.ForeignKey(blank=True, related_name='refunds', null=True, to='orders.Assistant')),
                ('order', models.ForeignKey(related_name='refunds', to='orders.Order')),
                ('user', models.ForeignKey(related_name='refunds', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='refundassistant',
            name='assistant',
        ),
        migrations.RemoveField(
            model_name='refundassistant',
            name='user',
        ),
        migrations.RemoveField(
            model_name='refundorder',
            name='order',
        ),
        migrations.RemoveField(
            model_name='refundorder',
            name='user',
        ),
        migrations.DeleteModel(
            name='RefundAssistant',
        ),
        migrations.DeleteModel(
            name='RefundOrder',
        ),
    ]
