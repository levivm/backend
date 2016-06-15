from django.conf.urls import url
from django.contrib import admin

from orders.models import Order, Assistant
from orders.views import RefundAdminTemplateView
from utils.mixins import OperativeModelAdminMixin


@admin.register(Order)
class OrderAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    search_fields = ('id',)
    list_display = ('id', 'activity_title', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'calendar__activity__title')
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
    list_display = ('name', 'order_num', 'activity_title', 'student')
    list_filter = ('order__calendar__activity__title',)
    search_fields = ('order__id',)
    raw_id_fields = ('order',)
    operative_readonly_fields = {'order'}

    def name(self, obj):
        return '%s %s' % (obj.first_name, obj.last_name)

    def order_num(self, obj):
        return obj.order.id

    def activity_title(self, obj):
        return obj.order.calendar.activity.title

    def student(self, obj):
        return obj.order.student.user.get_full_name()
