from django.contrib import admin

from organizers.models import Organizer, Instructor, OrganizerBankInfo
from utils.mixins import OperativeModelAdminMixin


@admin.register(Organizer)
class OrganizerAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'user','get_email')
    raw_id_fields = ('user',)
    operative_readonly_fields = {'user', 'rating'}

    def get_email(self, obj):
        return obj.user.email

    get_email.short_description = 'Email'



@admin.register(Instructor)
class InstructorAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('full_name', )
    operative_readonly_fields = {'organizer'}


@admin.register(OrganizerBankInfo)
class OrganizerBankInfoAdmin(OperativeModelAdminMixin, admin.ModelAdmin):
    list_display = ('organizer_name', 'account', 'bank')
    operative_readonly_fields = {'organizer'}

    def organizer_name(self, obj):
        return obj.organizer.name

