from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response

from locations.serializers import LocationsSerializer
from locations.models import Location
from activities.serializers import ActivitiesSerializer
from organizers.models import Instructor
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly
from .models import Organizer
from .serializers import OrganizersSerializer, InstructorsSerializer
from .permissions import IsCurrentUserSameOrganizer


def signup(request):
    return render(request, 'organizers/signup.html', {})


class OrganizerViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Organizer.objects.all()
    serializer_class = OrganizersSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )
    lookup_url_kwarg = 'organizer_pk'

    def activities(self, request, **kwargs):
        organizer = self.get_object()
        activities = organizer.activity_set.all()
        data = ActivitiesSerializer(activities, many=True).data
        return Response(data)



class OrganizerLocationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Location.objects.all()
    serializer_class = LocationsSerializer
    permission_classes = (IsAuthenticated, IsCurrentUserSameOrganizer, \
                          DjangoObjectPermissionsOrAnonReadOnly, )
    lookup_url_kwarg = 'organizer_pk'

    def set_location(self,request,organizer_pk=None):
        organizer = Organizer.objects.get(id=organizer_pk)
        location_data = request.data.copy()

        location_data['organizer'] = organizer.id

        location_serializer = LocationsSerializer(data=location_data,\
                                   context={'request': request,'organizer_location':True})
        if location_serializer.is_valid(raise_exception=True):
            organizer.locations.all().delete()
            location = location_serializer.save()
            organizer.locations.add(location)

        return Response(location_serializer.data)




class InstructorViewSet(viewsets.ModelViewSet):
    model = Instructor
    serializer_class = InstructorsSerializer
    lookup_url_kwarg = 'instructor_pk'
    permission_classes = (IsAuthenticated, DjangoObjectPermissions, )

    def get_queryset(self):
        organizer_id = self.kwargs.get('organizer_pk', None)
        organizer = get_object_or_404(Organizer, pk=organizer_id)
        return organizer.instructors.all()