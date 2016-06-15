from django.conf.urls import url
from django.contrib import admin

from orders.models import Order, Assistant
from orders.views import RefundAdminTemplateView
from utils.mixins import OperativeModelAdminMixin


@admin.register(Order)
class OrderAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    search_fields = ('id',)
    list_display = ('name', 'activity_title', 'status')
    list_filter = ('status',)
    raw_id_fields = ('calendar', 'student', 'payment')
    operative_readonly_fields = {'calendar', 'student', 'payment'}

    def get_urls(self):
        urls = super(OrderAdmin, self).get_urls()
        urls += [
            url(
                regex=r'^refunds/?$',
                view=self.admin_site.admin_view(RefundAdminTemplateView.as_view()),
                name='refunds'),
        ]
        return urls

    def name(self, obj):
        return obj.student.user.get_full_name()

    def activity_title(self, obj):
        return obj.calendar.activity.title


@admin.register(Assistant)
class AssistantAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    raw_id_fields = ('order',)
    operative_readonly_fields = {'order'}
