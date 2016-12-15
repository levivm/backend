from django.contrib import admin

from students.models import Student
from utils.mixins import OperativeModelAdminMixin


@admin.register(Student)
class StudentAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('email', 'name', 'telephone', 'created_at')
    operative_readonly_fields = {'user', 'referrer_code'}

    def email(self, obj):
        return obj.user.email

    def name(self, obj):
        return obj.user.get_full_name()
