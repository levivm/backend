from django.shortcuts import render
from rest_framework import viewsets
from .models import City
from .serializers import CitiesSerializer





class CitiesViewSet(viewsets.ModelViewSet):

    queryset = City.objects.all()
    serializer_class = CitiesSerializer


# Create your views here.
