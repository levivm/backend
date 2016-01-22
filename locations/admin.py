from django.contrib.gis import admin

from locations.models import Location, City


@admin.register(Location)
class LocationAdmin(admin.OSMGeoAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.OSMGeoAdmin):
    pass
