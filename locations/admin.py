from django.contrib.gis import admin

from locations.models import Location, City
from utils.mixins import OperativeModelAdminMixin


@admin.register(Location)
class LocationAdmin(OperativeModelAdminMixin, admin.OSMGeoAdmin):
    list_display = ('id', 'address', 'first_activity')
    operative_readonly_fields = {'organizer'}

    def first_activity(self, obj):
        return obj.activity_set.first()


@admin.register(City)
class CityAdmin(OperativeModelAdminMixin, admin.OSMGeoAdmin):
    list_display = ('name',)
    operative_readonly_fields = {'name', 'order', 'point'}
