from ast import literal_eval

from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Location,City


#from django.contrib.gis.geos import Point, fromstr



# this will be used when postgis is enabled.
# class PointField(serializers.Field):
#     """
#     PointField 
#     """
#     def to_representation(self, obj):
#         return [obj[0],obj[1]]

#     def to_internal_value(self, data):
#         point = fromstr("POINT(%s %s)" % (data[1], data[0]))
#         return point



class PointStrField(serializers.Field):
    """
    String Point Field 
    """
    def to_representation(self, obj):
        coords = literal_eval(obj)
        return [coords[0],coords[1]]

    def to_internal_value(self, data):
        point  =  "(%s,%s)" % (data[0], data[1])
        return point


class CitiesSerializer(GeoFeatureModelSerializer):
    # point = PointStrField()
    class Meta:
        model = City
        geo_field = "point"
        fields = (
            'id',
            'name',
            # 'point'
            )



class LocationsSerializer(GeoFeatureModelSerializer):
    city  = serializers.SlugRelatedField(slug_field='id',queryset=City.objects.all(),required=True)
    # point = PointStrField()

    class Meta:
        model = Location
        geo_field = "point"
        fields = (
            'id',
            'city',
            # 'point',
            'address',
            'organizer'
            )

    def create(self,validated_data):
        is_organizer_location = self.context.get('organizer_location')
        instance = super(LocationsSerializer,self).create(validated_data)
        
        if not is_organizer_location:
            return instance

        return instance
