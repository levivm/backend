from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, DjangoObjectPermissions
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied


from activities.mixins import ActivityCardMixin
from activities.models import Activity
from activities.permissions import IsActivityOwner


from locations.serializers import LocationsSerializer
from locations.models import Location
from activities.serializers import ActivitiesSerializer, ActivitiesCardSerializer
from organizers.models import Instructor, OrganizerBankInfo
from organizers.serializers import OrganizerBankInfoSerializer
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly, IsOrganizer, \
                              UnpublishedActivitiesOnlyForOwner
from utils.paginations import SmallResultsSetPagination

from .models import Organizer
from .serializers import OrganizersSerializer, InstructorsSerializer
from .permissions import IsCurrentUserSameOrganizer


def signup(request):
    return render(request, 'organizers/signup.html', {})


class OrganizerViewSet(ActivityCardMixin, viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Organizer.objects.all()
    serializer_class = OrganizersSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, \
                          UnpublishedActivitiesOnlyForOwner)
    lookup_url_kwarg = 'organizer_pk'

    def activities(self, request, **kwargs):
        organizer = self.get_object()
        status = request.query_params.get('status')
        activities = organizer.get_activities_by_status(status)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitiesSerializer(page, many=True,
                                              context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        serializer = ActivitiesSerializer(activities, many=True, 
                                          context=self.get_serializer_context())
        result = serializer.data
        return Response(result)


class OrganizerLocationViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Location.objects.all()
    serializer_class = LocationsSerializer
    permission_classes = (IsAuthenticated, IsCurrentUserSameOrganizer,
                          DjangoObjectPermissionsOrAnonReadOnly,)
    lookup_url_kwarg = 'organizer_pk'

    def set_location(self, request, organizer_pk=None):
        organizer = Organizer.objects.get(id=organizer_pk)
        location_data = request.data.copy()

        location_data['organizer'] = organizer.id

        location_serializer = LocationsSerializer(data=location_data,
                                                  context={'request': request,
                                                           'organizer_location': True})
        if location_serializer.is_valid(raise_exception=True):
            organizer.locations.all().delete()
            location = location_serializer.save()
            organizer.locations.add(location)
        return Response(location_serializer.data)


class OrganizerInstructorViewSet(viewsets.ModelViewSet):
    model = Instructor
    serializer_class = InstructorsSerializer
    permission_classes = (IsAuthenticated, IsCurrentUserSameOrganizer, DjangoObjectPermissions,)
    pagination_class = PageNumberPagination

    def get_queryset(self):
        organizer_id = self.kwargs.get('organizer_pk', None)
        organizer = get_object_or_404(Organizer, pk=organizer_id)
        return organizer.instructors.all()


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorsSerializer
    permission_classes = (IsAuthenticated, IsOrganizer, DjangoObjectPermissions)


class ActivityInstructorViewSet(viewsets.ModelViewSet):
    model = Instructor
    serializer_class = InstructorsSerializer
    permission_classes = (IsAuthenticated, IsActivityOwner, DjangoObjectPermissions)
    ERROR = {
        'max_instructors': _('La actividad ya ha alcanzado el máximo de instructores.'),
    }

    def get_activity(self):
        return get_object_or_404(Activity, pk=self.kwargs.get('activity_pk'))

    def get_queryset(self):
        activity = self.get_activity()
        return activity.instructors.all()

    def create(self, request, *args, **kwargs):
        activity = self.get_activity()
        if activity.can_associate_instructor():
            response = super(ActivityInstructorViewSet, self).create(request, *args, **kwargs)
            instructor = Instructor.objects.get(id=response.data['id'])
            activity.instructors.add(instructor)
            return response

        return Response(self.ERROR['max_instructors'], status=status.HTTP_400_BAD_REQUEST)

    def get_object(self):
        obj = get_object_or_404(Instructor, pk=self.kwargs.get('pk'))
        self.check_object_permissions(self.request, obj)
        return obj

    def update(self, request, *args, **kwargs):
        activity = self.get_activity()
        if activity.can_associate_instructor():
            response = super(ActivityInstructorViewSet, self).update(request, *args, **kwargs)
            instructor = self.get_object()
            activity.instructors.add(instructor)
            return response

        return Response(self.ERROR['max_instructors'], status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instructor = self.get_object()
        activity = self.get_activity()
        activity.instructors.remove(instructor)
        return Response(status=status.HTTP_204_NO_CONTENT)


class OrganizerBankInfoViewSet(viewsets.ModelViewSet):
    queryset = OrganizerBankInfo.objects.all()
    serializer_class = OrganizerBankInfoSerializer
    permission_classes = (IsAuthenticated, IsOrganizer)

    def get_object(self):
        try:
            return self.request.user.organizer_profile.bank_info
        except OrganizerBankInfo.DoesNotExist:
            return None

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance:
            return Response({})

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class OrganizerBankInfoChoicesViewSet(viewsets.GenericViewSet):
    serializer_class = OrganizerBankInfoSerializer
    permission_classes = (IsAuthenticated, IsOrganizer)

    def choices(self, request, *args, **kwargs):
        return Response(OrganizerBankInfo.get_choices())
