from django.contrib import admin

from organizers.models import Organizer, Instructor, OrganizerBankInfo


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    raw_id_fields = ('user',)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('full_name', )


@admin.register(OrganizerBankInfo)
class OrganizerBankInfoAdmin(admin.ModelAdmin):
    list_display = ('organizer_name', 'account', 'bank')

    def organizer_name(self, obj):
        return obj.organizer.name

