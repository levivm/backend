from rest_framework import serializers
from locations.serializers import CitiesSerializer
from locations.models import City

class ContactFormsSerializer(serializers.Serializer):

    name     = serializers.CharField(max_length=200)
    topic    = serializers.CharField(max_length=200)
    subtopic = serializers.CharField(max_length=400)
    email   = serializers.EmailField()
    phone_number = serializers.CharField(max_length=200)
    city = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)



