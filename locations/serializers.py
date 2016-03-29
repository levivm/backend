from rest_framework import serializers
from .models import Location, City


class PointStrField(serializers.Field):
    """
    String Point Field
    """
    def to_representation(self, obj):
        latitude = obj.coords[0]
        longitude = obj.coords[1]
        return [latitude, longitude]

    def to_internal_value(self, data):
        point = "POINT(%s %s)" % (data[0], data[1])
        return point


class CitiesSerializer(serializers.ModelSerializer):
    point = PointStrField()

    class Meta:
        model = City
        geo_field = "point"
        fields = (
            'id',
            'name',
            'point'
            )


class LocationsSerializer(serializers.ModelSerializer):
    city = serializers.SlugRelatedField(slug_field='id', queryset=City.objects.all(),
                                        required=True)
    point = PointStrField()

    class Meta:
        model = Location
        fields = (
            'id',
            'city',
            'point',
            'address',
            'organizer'
            )

    def create(self, validated_data):
        is_organizer_location = self.context.get('organizer_location')
        instance = super(LocationsSerializer, self).create(validated_data)

        if not is_organizer_location:
            return instance

        return instance
