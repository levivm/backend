from rest_framework import viewsets

from .models import City
from .serializers import CitiesSerializer
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly


class CitiesViewSet(viewsets.ModelViewSet):
    queryset = City.objects.all()
    serializer_class = CitiesSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )
