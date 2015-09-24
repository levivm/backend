# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def gen_code(apps, schema_editor):
    Student = apps.get_model('students', 'Student')
    for student in Student.objects.all():
        student.referrer_code = 'student%s' % (student.id)
        student.save(update_fields=['referrer_code'])


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_student_referrer_code'),
    ]

    operations = [
        migrations.RunPython(gen_code,
                             reverse_code=migrations.RunPython.noop)
    ]
