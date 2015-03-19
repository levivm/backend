from .models import Location,City
from ast import literal_eval
from rest_framework import serializers
#from django.contrib.gis.geos import Point, fromstr



# this will be used when postgis is enabled.
class PointField(serializers.Field):
    """
    PointField 
    """
    def to_representation(self, obj):
        return [obj[0],obj[1]]

    def to_internal_value(self, data):
        point = fromstr("POINT(%s %s)" % (data[1], data[0]))
        return point



class PointStrField(serializers.Field):
    """
    String Point Field 
    """
    def to_representation(self, obj):
        coords = literal_eval(obj)
        return [coords[0],coords[1]]

    def to_internal_value(self, data):
        point  =  "(%s,%s)" % (data[1], data[0])
        return point


class CitiesSerializer(serializers.ModelSerializer):
    point = PointStrField()
    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'point'
            )


class LocationsSerializer(serializers.ModelSerializer):
    city  = serializers.SlugRelatedField(slug_field='id',queryset=City.objects.all(),required=True)
    point = PointStrField()
    class Meta:
        model = Location
        fields = (
            'id',
            'city',
            'point',
            'address'
            )
