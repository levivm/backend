# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import utils.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0003_organizer_headline'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('short_description', models.CharField(max_length=300)),
                ('level', models.CharField(choices=[('P', 'Principiante'), ('I', 'Intermedio'), ('A', 'Avanzado'), ('N', 'No Aplica')], max_length=1)),
                ('goals', models.TextField(blank=True)),
                ('methodology', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('audience', models.TextField(blank=True)),
                ('requirements', models.TextField(blank=True)),
                ('return_policy', models.TextField(blank=True)),
                ('extra_info', models.TextField(blank=True)),
                ('youtube_video_url', models.CharField(max_length=200, null=True, blank=True)),
                ('published', models.NullBooleanField(default=False)),
                ('certification', models.NullBooleanField(default=False)),
                ('score', models.FloatField(default=0)),
                ('instructors', models.ManyToManyField(to='organizers.Instructor', related_name='activities')),
            ],
            options={
                'abstract': False,
            },
            bases=(utils.mixins.AssignPermissionsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='ActivityPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('photo', models.ImageField(upload_to='activities')),
                ('main_photo', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(to='activities.Activity', related_name='pictures')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityStockPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('photo', models.ImageField(upload_to='activities_stock')),
            ],
        ),
        migrations.CreateModel(
            name='Calendar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('initial_date', models.DateTimeField()),
                ('closing_sale', models.DateTimeField()),
                ('number_of_sessions', models.IntegerField()),
                ('session_price', models.FloatField()),
                ('capacity', models.IntegerField()),
                ('enroll_open', models.NullBooleanField(default=True)),
                ('is_weekend', models.NullBooleanField(default=False)),
                ('is_free', models.BooleanField(default=False)),
                ('activity', models.ForeignKey(to='activities.Activity', related_name='calendars')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CalendarSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date', models.DateTimeField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('calendar', models.ForeignKey(to='activities.Calendar', related_name='sessions')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('color', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(to='activities.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=100, unique=True)),
                ('occurrences', models.IntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='activitystockphoto',
            name='sub_category',
            field=models.ForeignKey(to='activities.SubCategory'),
        ),
    ]
