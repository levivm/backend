from django.contrib import admin

from orders.models import Order, Assistant


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity_title', 'status')
    list_filter = ('status',)
    raw_id_fields = ('calendar', 'student', 'payment')

    def name(self, obj):
        return obj.student.user.get_full_name()

    def activity_title(self, obj):
        return obj.calendar.activity.title


@admin.register(Assistant)
class AssistantAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    raw_id_fields = ('order',)
