# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from activities.permissions import IsActivityOwnerOrReadOnly
from activities.tasks import SendEmailChronogramTask, SendEmailLocationTask

from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly
from .models import Activity, Category, SubCategory, Tags, Chronogram, ActivityPhoto
from .permissions import IsActivityOwner
from .serializers import ActivitiesSerializer, CategoriesSerializer, SubCategoriesSerializer, \
    TagsSerializer, ChronogramsSerializer, ActivityPhotosSerializer
from locations.serializers import LocationsSerializer


class ChronogramsViewSet(viewsets.ModelViewSet):
    serializer_class = ChronogramsSerializer
    lookup_url_kwarg = 'calendar_pk'
    model = Chronogram
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)

    def get_queryset(self):
        activity_id = self.kwargs.get('activity_pk', None)
        activity = get_object_or_404(Activity, pk=activity_id)
        return activity.chronograms.all()

    def list(self, request, *args, **kwargs):
        chronograms = self.get_queryset().order_by('initial_date')
        if request.GET.get('actives'):
            chronograms = chronograms.filter(initial_date__gt=now())

        chronogram_serializer = self.serializer_class(chronograms, many=True)
        return Response(chronogram_serializer.data)

    def destroy(self, request, *args, **kwargs):
        chronogram = self.get_object()
        if chronogram.orders.count() == 0:
            return super().destroy(request, *args, **kwargs)

        return Response({'detail': _('No puede eliminar este calendario, tiene estudiantes inscritos, contactanos.')},
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        chronogram = self.get_object()
        task = SendEmailChronogramTask()
        task.apply_async((chronogram.id,), countdown=1800)
        return result


class ActivitiesViewSet(viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitiesSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwnerOrReadOnly)
    lookup_url_kwarg = 'activity_pk'

    def delete_calendar(self, request, pk=None):

        chronogram_id = request.GET.get('id', None)

        activity = self.get_object()
        try:
            chronogram = activity.chronograms.get(id=chronogram_id)
        except Chronogram.DoesNotExist:
            msg = _("El Calendario a borrar no existe")
            return Response({str(chronogram_id): msg}, status=status.HTTP_404_NOT_FOUND)

        chronogram.delete()
        return Response({'chronogram_id': chronogram_id}, status=status.HTTP_200_OK)

    def get_calendars(self, request, pk=None):
        activity = self.get_object()
        chronogram = activity.chronograms.all()
        chronogram_serializer = chronogram_serializer = ChronogramsSerializer(chronogram, many=True)
        return Response(chronogram_serializer.data)

    def update_calendar(self, request, **kwargs):

        data = request.DATA
        chronogram_id = data.get("id", None)
        activity = self.get_object()

        try:
            chronogram = activity.chronograms.get(id=chronogram_id)
        except Chronogram.DoesNotExist:
            msg = _("El calendario a editar no existe")
            return Response({'non_field_errors': [msg]}, status=status.HTTP_404_NOT_FOUND)

        chronogram = activity.chronograms.get(id=chronogram_id)
        chronogram_serializer = ChronogramsSerializer(chronogram, data=data, context={'request': request})
        chronogram = None
        if chronogram_serializer.is_valid(raise_exception=True):
            chronogram = chronogram_serializer.save()
        return Response(chronogram_serializer.data)

    def create_calendar(self, request, pk=None):

        data = request.DATA

        chronogram_serializer = ChronogramsSerializer(data=data, context={'request': request})
        chronogram = None
        if chronogram_serializer.is_valid(raise_exception=True):
            chronogram = chronogram_serializer.save()
        return Response(chronogram_serializer.data)

    def set_location(self, request, *args, **kwargs):
        activity = self.get_object()
        location_data = request.data.copy()
        location_serializer = LocationsSerializer(data=location_data)
        if location_serializer.is_valid(raise_exception=True):
            location = location_serializer.save()
            activity.set_location(location)
            task = SendEmailLocationTask()
            task.apply_async((activity.id,), countdown=1800)

        return Response(location_serializer.data)

    def general_info(self, request):
        categories = Category.objects.all()
        sub_categories = SubCategory.objects.all()
        tags = Tags.ready_to_use()
        levels = Activity.get_levels()

        data = {
            'categories': CategoriesSerializer(categories, many=True).data,
            'subcategories': SubCategoriesSerializer(sub_categories, many=True).data,
            'levels': levels,
            'tags': TagsSerializer(tags, many=True).data,

        }

        return Response(data)

    def publish(self, request, **kwargs):
        activity = self.get_object()
        published = activity.publish()

        if not published:
            msg = _("No ha completado todos los pasos para publicar")
            return Response({'detail': msg}, status.HTTP_400_BAD_REQUEST)
        return Response(status.HTTP_200_OK)

    def unpublish(self, request, **kwargs):
        activity = self.get_object()
        activity.unpublish()
        return Response(status.HTTP_200_OK)


class ActivityPhotosViewSet(viewsets.ModelViewSet):
    model = ActivityPhoto
    serializer_class = ActivityPhotosSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwner)
    lookup_url_kwarg = 'gallery_pk'

    def get_queryset(self):
        activity = self.get_activity_object(**self.kwargs)
        return activity.photos.all()

    def create(self, request, *args, **kwargs):
        activity = self.get_activity_object(**kwargs)
        serializer = ActivityPhotosSerializer(data=request.data, context={'activity': activity, 'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        activity_serializer = self.get_activity_serializer(instance=activity, context={'request': request})
        return Response(
            data={'activity': activity_serializer.data, 'photo': serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers)

    def destroy(self, request, *args, **kwargs):
        gallery_pk = kwargs.get('gallery_pk')
        activity = self.get_activity_object(**kwargs)
        activity_serializer = self.get_activity_serializer(instance=activity, context={'request': request})
        instance = self.get_object()
        if instance.main_photo:
            msg = _("No puede eliminar la foto principal")
            return Response({'detail': msg}, status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        return Response(
            data={'activity': activity_serializer.data, 'photo_id': gallery_pk},
            status=status.HTTP_200_OK)

    def get_activity_object(self, **kwargs):
        activity_pk = kwargs.get('activity_pk')
        return get_object_or_404(Activity, pk=activity_pk)

    def get_activity_serializer(self, instance, context):
        return ActivitiesSerializer(instance=instance, context=context)


class CategoriesViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoriesSerializer


class SubCategoriesViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoriesSerializer


class TagsViewSet(viewsets.ModelViewSet):
    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,)


class ListCategories(APIView):
    """
    View to list all users in the system.

    * Requires token authentication.
    * Only admin users are able to access this view.
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        categories = Category.objects.all()
        subcategories = SubCategory.objects.all()
        data = {
            'categories': CategoriesSerializer(categories, many=True).data,
            'subcategory': SubCategoriesSerializer(subcategories, many=True).data,
        }
        return Response(data)
