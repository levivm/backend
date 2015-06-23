from .models import Location,City
from ast import literal_eval
from rest_framework import serializers
from utils.mixins import AssignPermissionsMixin
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


class CitiesSerializer(serializers.ModelSerializer):
    point = PointStrField()
    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'point'
            )



class LocationsSerializer(AssignPermissionsMixin,serializers.ModelSerializer):
    city  = serializers.SlugRelatedField(slug_field='id',queryset=City.objects.all(),required=True)
    point = PointStrField()
    permissions = ('locations.change_location','locations.add_location','locations.delete_location', )


    class Meta:
        model = Location
        fields = (
            'id',
            'city',
            'point',
            'address',
            'organizer'
            )

    def create(self,validated_data):
        is_organizer_location = self.context.get('organizer_location')
        instance = super(LocationsSerializer,self).create(validated_data)
        
        if not is_organizer_location:
            return instance

        request = self.context.get('request')

        self.assign_permissions(request.user, instance)
        return instance


