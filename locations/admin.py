from django.contrib.gis import admin

from locations.models import Location, City
from utils.mixins import OperativeModelAdminMixin


@admin.register(Location)
class LocationAdmin(OperativeModelAdminMixin, admin.OSMGeoAdmin):
    operative_readonly_fields = {'organizer'}


@admin.register(City)
class CityAdmin(OperativeModelAdminMixin, admin.OSMGeoAdmin):
    operative_readonly_fields = {'name', 'order', 'point'}
