# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activities', '0001_initial'),
        ('payments', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assistant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('token', models.CharField(max_length=20, unique=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254, blank=True)),
                ('enrolled', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('amount', models.FloatField()),
                ('quantity', models.IntegerField()),
                ('status', models.CharField(choices=[('approved', 'Aprobada'), ('pending', 'Pendiente'), ('cancelled', 'Cancelada'), ('declined', 'Declinada')], max_length=15, default='pending')),
                ('calendar', models.ForeignKey(to='activities.Calendar', related_name='orders')),
                ('payment', models.OneToOneField(to='payments.Payment', null=True)),
                ('student', models.ForeignKey(to='students.Student', related_name='orders')),
            ],
        ),
        migrations.CreateModel(
            name='RefundAssistant',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('status', models.CharField(choices=[('approved', 'Approved'), ('pending', 'Pending'), ('declined', 'Declined')], max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('response_at', models.DateTimeField()),
                ('assistant', models.ForeignKey(to='orders.Assistant')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RefundOrder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
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
            name='order',
            field=models.ForeignKey(to='orders.Order', related_name='assistants'),
        ),
    ]
