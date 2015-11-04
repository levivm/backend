from django.contrib import admin

from payments.models import Fee


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    pass
