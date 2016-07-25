# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-07-21 17:02
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


def slugify_categories(apps, schema_editor):
    Category = apps.get_model("activities", "Category")
    for category in Category.objects.all():
        if not category.slug:
            category.slug = slugify(category.name)
            category.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('activities', '0009_auto_20160721_1140'),
    ]

    operations = [
        migrations.RunPython(slugify_categories),
    ]