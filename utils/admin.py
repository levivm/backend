from django.contrib import admin

from utils.mixins import OperativeModelAdminMixin
from utils.models import EmailTaskRecord


@admin.register(EmailTaskRecord)
class EmailTaskRecordAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    operative_readonly_fields = {'to', 'template_name', 'subject', 'data', 'status',
                                 'reject_reason', 'task_id', 'smtp_id'}
