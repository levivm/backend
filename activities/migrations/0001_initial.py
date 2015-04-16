# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organizers', '0001_initial'),
        ('locations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('type', models.CharField(max_length=2, choices=[('CU', 'Curso'), ('CE', 'Certificación'), ('CL', 'Clase'), ('DP', 'Diplomado'), ('SE', 'Seminario'), ('TA', 'Taller')])),
                ('title', models.CharField(max_length=100)),
                ('large_description', models.TextField()),
                ('short_description', models.CharField(max_length=100)),
                ('level', models.CharField(max_length=1, choices=[('P', 'Principiante'), ('I', 'Intermedio'), ('A', 'Avanzado'), ('N', 'No Aplica')])),
                ('goals', models.TextField(blank=True)),
                ('methodology', models.TextField(blank=True)),
                ('content', models.TextField(blank=True)),
                ('audience', models.TextField(blank=True)),
                ('requirements', models.TextField(blank=True)),
                ('return_policy', models.TextField(blank=True)),
                ('extra_info', models.TextField(blank=True)),
                ('youtube_video_url', models.CharField(blank=True, null=True, max_length=200)),
                ('enroll_open', models.NullBooleanField(default=True)),
                ('published', models.NullBooleanField(default=False)),
                ('instructors', models.ManyToManyField(related_name='activities', to='organizers.Instructor')),
                ('location', models.ForeignKey(null=True, to='locations.Location')),
                ('organizer', models.ForeignKey(to='organizers.Organizer')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityPhoto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('photo', models.ImageField(upload_to='activities')),
                ('activity', models.ForeignKey(related_name='photos', to='activities.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Chronogram',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('initial_date', models.DateTimeField()),
                ('closing_sale', models.DateTimeField()),
                ('number_of_sessions', models.IntegerField()),
                ('session_price', models.FloatField()),
                ('capacity', models.IntegerField()),
                ('activity', models.ForeignKey(related_name='chronograms', to='activities.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('description', models.CharField(max_length=200)),
                ('author', models.CharField(max_length=200)),
                ('rating', models.IntegerField()),
                ('attributes', models.CharField(max_length=200)),
                ('activity', models.ForeignKey(to='activities.Activity')),
            ],
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('date', models.DateTimeField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('chronogram', models.ForeignKey(related_name='sessions', to='activities.Chronogram')),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('category', models.ForeignKey(to='activities.Category')),
            ],
        ),
        migrations.CreateModel(
            name='Tags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('occurrences', models.IntegerField(default=1)),
            ],
        ),
        migrations.AddField(
            model_name='activity',
            name='sub_category',
            field=models.ForeignKey(to='activities.SubCategory'),
        ),
        migrations.AddField(
            model_name='activity',
            name='tags',
            field=models.ManyToManyField(to='activities.Tags'),
        ),
    ]
