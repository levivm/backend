from django.contrib import admin

from organizers.models import Organizer


@admin.register(Organizer)
class OrganizerAdmin(admin.ModelAdmin):
    pass
