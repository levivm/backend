from django.contrib.gis.db import models

from organizers.models import Organizer
from utils.mixins import AssignPermissionsMixin


class City(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    point = models.PointField(help_text="Represented as (longitude, latitude)")

    objects = models.GeoManager()

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class Location(AssignPermissionsMixin, models.Model):
    address = models.TextField()
    city = models.ForeignKey(City)
    point = models.PointField(help_text="Represented as (longitude, latitude)")
    organizer = models.ForeignKey(Organizer, blank=True, null=True, related_name="locations")

    permissions = ('locations.change_location', 'locations.add_location',
                   'locations.delete_location')

    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        if self.organizer:
            super(Location, self).save(user=self.organizer.user, obj=self, *args, **kwargs)
        else:
            models.Model.save(self, *args, **kwargs)
