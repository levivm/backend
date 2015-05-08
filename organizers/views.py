from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from .models import Organizer
from .serializers import OrganizersSerializer,InstructorsSerializer
from locations.serializers import LocationsSerializer
from rest_framework.response import Response
from activities.serializers import ActivitiesSerializer
from organizers.models import Instructor
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly



def signup(request):
    return render(request, 'organizers/signup.html', {})


class OrganizerViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Organizer.objects.all()
    serializer_class = OrganizersSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )

    def activities(self, request, **kwargs):
        organizer = self.get_object()
        activities = organizer.activity_set.all()
        data = ActivitiesSerializer(activities, many=True).data
        return Response(data)

    def set_location(self,request,pk=None):
        organizer = self.get_object()

        location_data = request.data.copy()
        location_data['organizer'] = organizer.id
        location_serializer = LocationsSerializer(data=location_data)
        if location_serializer.is_valid(raise_exception=True):
            organizer.locations.all().delete()
            location = location_serializer.save()
            organizer.locations.add(location)
            

        return Response(location_serializer.data)


class InstructorViewSet(viewsets.ModelViewSet):
    model = Instructor
    serializer_class = InstructorsSerializer
    lookup_url_kwarg = 'instructor_id'
    permission_classes = (IsAuthenticated, DjangoObjectPermissions, )

    def get_queryset(self):
        organizer_id = self.kwargs.get('organizer_id', None)
        organizer = get_object_or_404(Organizer, pk=organizer_id)
        return organizer.instructors.all()