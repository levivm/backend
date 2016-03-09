from rest_framework import serializers


class ContactFormsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    topic = serializers.CharField(max_length=200)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=1000)
