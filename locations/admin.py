from django.contrib import admin

from locations.models import Location, City


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass
