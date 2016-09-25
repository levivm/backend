import datetime

from django.contrib import admin

from organizers.models import Organizer, Instructor, OrganizerBankInfo
from utils.mixins import OperativeModelAdminMixin


class OpenedActivitiesListFilter(admin.SimpleListFilter):
    title = 'Estado de actividades'
    parameter_name = 'opened_activities'

    def lookups(self, request, model_admin):
        return (
            ('opened', 'Abiertas'),
            ('closed', 'Cerradas'),
            ('unpublished', 'Sin publicar')
        )

    def queryset(self, request, queryset):
        today = datetime.datetime.today().date()
        if self.value() == 'opened':
            return queryset.filter(activity__calendars__initial_date__gte=today,
                                   activity__published=True)
        elif self.value() == 'closed':
            return queryset.filter(activity__calendars__initial_date__lt=today,
                                   activity__published=True)
        elif self.value() == 'unpublished':
            return queryset.filter(activity__published=False)


@admin.register(Organizer)
class OrganizerAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name','get_email', 'rating', 'opened_activities', 'total_activities')
    list_filter = (OpenedActivitiesListFilter,)
    raw_id_fields = ('user',)
    operative_readonly_fields = {'user', 'rating'}

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'

    def opened_activities(self, obj):
        return obj.get_activities_by_status().count()

    def total_activities(self, obj):
        return obj.activity_set.count()


@admin.register(Instructor)
class InstructorAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('full_name', 'organizer')
    list_filter = ('organizer', 'activities__title')
    operative_readonly_fields = {'organizer'}


@admin.register(OrganizerBankInfo)
class OrganizerBankInfoAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'organizer_name')
    operative_readonly_fields = {'organizer'}

    def organizer_name(self, obj):
        return obj.organizer.name

