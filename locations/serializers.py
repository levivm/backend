from .models import Location,City
from django.contrib.gis.geos import Point, fromstr

from rest_framework import serializers



class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = (
            'id',
            'name',
            'point'
            )

    def validate_point(self, value):
        #raise serializers.ValidationError("Usuario no es organizador")
        point = fromstr("POINT(%s %s)" % (value[0], value[1]))
        return point

class LocationsSerializer(serializers.ModelSerializer):
    city  = serializers.SlugRelatedField(slug_field='id',queryset=City.objects.all(),required=True)
    class Meta:
        model = Location
        fields = (
            'id',
            'city',
            'point',
            'address'
            )
        depth = 1


    def validate_point(self, value):
        print "asdasdasdasd",value
        #raise serializers.ValidationError("Usuario no es organizador")
        point = fromstr("POINT(%s %s)" % (value[0], value[1]))
        return point

    # def validate_city(self,value):
    #     print "ASDASDASDDDDDDDDDDDDDDDDDDDDDD",value
    #     return value

    def validate_name(self,value):
        #raise serializers.ValidationError("Usuario no es organizador")
        return value

    # def create(self, validated_data):
    #     print "wwWWWWWWWWWWW",validated_data
    #     # request = self.context['request']
    #     # _tags = request.DATA.getlist('tags[]')

    #     # tags  = Tags.update_or_create(_tags)
    #     # if 'category' in validated_data:
    #     #     del validated_data['category']
    #     # activity = Location.objects.create(**validated_data)
    #     # activity.tags.clear()
    #     # activity.tags.add(*tags)
    #     activity = None
    #     return activity