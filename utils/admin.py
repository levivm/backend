from django.contrib import admin

from utils.models import EmailTaskRecord


@admin.register(EmailTaskRecord)
class EmailTaskRecordAdmin(admin.ModelAdmin):
    pass
