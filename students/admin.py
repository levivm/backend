from django.contrib import admin

from students.models import Student
from utils.mixins import OperativeModelAdminMixin


@admin.register(Student)
class StudentAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'user', 'referrer_code'}
