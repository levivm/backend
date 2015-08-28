from django.db import models
from organizers.models import Organizer

# Create your models here.


class City(models.Model):
    #country = models.ForeignKey(Country)
    name  = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    point = models.CharField(max_length="200")
    #point = models_gis.PointField(help_text="Represented as (longitude, latitude)")
    #objects = models_gis.GeoManager()

    class Meta:
        verbose_name_plural = "cities"

    def __str__(self):
        return self.name


class Location(models.Model):

    address = models.TextField()
    city    = models.ForeignKey(City)
    point   = models.CharField(max_length="200")
    organizer = models.ForeignKey(Organizer,null=True,related_name="locations")
    # Automatically create slug based on the name field
    #slug = AutoSlugField(populate_from='name', max_length=255)
      
    # Geo Django field to store a point

    #point = models_gis.PointField(help_text="Represented as (longitude, latitude)")
    # You MUST use GeoManager to make Geo Queries
    #objects = models_gis.GeoManager()



# class Country(models.Model):
#     code = models.CharField(max_length=3)
#     name = models.CharField(max_length=100)
#     order = models.IntegerField(default=0)
#     #location = models.ForeignKey(Location)

#     class Meta:
#         verbose_name_plural = "countries"

#     def __unicode__(self):
#         return self.name



