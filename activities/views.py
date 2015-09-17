# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
from django.db.models.aggregates import Count
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from activities.mixins import CalculateActivityScoreMixin
from activities.permissions import IsActivityOwnerOrReadOnly
from activities.searchs import ActivitySearchEngine
from activities.tasks import SendEmailChronogramTask, SendEmailLocationTask

from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly
from .models import Activity, Category, SubCategory, Tags, Chronogram, ActivityPhoto,\
                    ActivityStockPhoto
from .permissions import IsActivityOwner
from .serializers import ActivitiesSerializer, CategoriesSerializer, SubCategoriesSerializer, \
    TagsSerializer, ChronogramsSerializer, ActivityPhotosSerializer
from locations.serializers import LocationsSerializer


class ChronogramsViewSet(viewsets.ModelViewSet):
    serializer_class = ChronogramsSerializer
    lookup_url_kwarg = 'calendar_pk'
    model = Chronogram
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly,IsActivityOwnerOrReadOnly)

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


class ActivitiesViewSet(CalculateActivityScoreMixin, viewsets.ModelViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitiesSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwnerOrReadOnly)
    lookup_url_kwarg = 'activity_pk'

    def partial_update(self, request, *args, **kwargs):
        response = super(ActivitiesViewSet, self).partial_update(request, *args, **kwargs)
        self.calculate_score(kwargs[self.lookup_url_kwarg])
        return response

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


class ActivityPhotosViewSet(CalculateActivityScoreMixin, viewsets.ModelViewSet):
    model = ActivityPhoto
    serializer_class = ActivityPhotosSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwner)
    lookup_url_kwarg = 'gallery_pk'

    def get_queryset(self):
        activity = self.get_activity_object(**self.kwargs)
        return activity.photos.all()

    def create(self, request, *args, **kwargs):
        activity       = self.get_activity_object(**kwargs)
        # is_stock_image = request.data.get('is_stock_image',False)

        serializer = ActivityPhotosSerializer(data=request.data, \
                            context={'activity': activity, \
                                     'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.calculate_score(activity_id=activity.id)
        headers = self.get_success_headers(serializer.data)
        activity_serializer = self.get_activity_serializer(instance=activity, \
                                context={'request': request})
        return Response(
            data={'activity': activity_serializer.data, 'picture': serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers)


    def set_cover_from_stock(self,request,*args,**kwargs):
        activity   = self.get_activity_object(**kwargs)
        cover_id = request.data.get('cover_id')
        stock_cover_picture = get_object_or_404(ActivityStockPhoto, pk=cover_id)
        photo = ActivityPhoto.create_from_stock(stock_cover_picture,activity)

        serializer = ActivityPhotosSerializer(instance=photo)

        # self.calculate_score(activity_id=activity.id)
        headers = self.get_success_headers(serializer.data)
        activity_serializer = self.get_activity_serializer(instance=activity, \
                                context={'request': request})
        return Response(
            data={'activity': activity_serializer.data, 'picture': serializer.data},
            status=status.HTTP_201_CREATED,
            headers=headers)



    def destroy(self, request, *args, **kwargs):
        gallery_pk = kwargs.get('gallery_pk')
        activity = self.get_activity_object(**kwargs)
        activity_serializer = self.get_activity_serializer(instance=activity, \
                                context={'request': request})
        instance = self.get_object()
        if instance.main_photo:
            msg = _("No puede eliminar la foto principal")
            return Response({'detail': msg}, status=status.HTTP_200_OK)
        self.perform_destroy(instance)
        self.calculate_score(activity_id=activity.id)
        return Response(
            data={'activity': activity_serializer.data, 'photo_id': gallery_pk},
            status=status.HTTP_200_OK)

    def get_activity_object(self, **kwargs):
        activity_pk = kwargs.get('activity_pk')
        return get_object_or_404(Activity, pk=activity_pk)

    def get_activity_serializer(self, instance, context):
        return ActivitiesSerializer(instance=instance, context=context)


class CategoriesViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriesSerializer

    def get_queryset(self):
        return Category.objects.all().order_by('name')


class SubCategoriesViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoriesSerializer


    def get_pool_from_stock(self,request,*args, **kwargs):
        sub_category_id = kwargs.get('subcategory_id')
        photos     = ActivityStockPhoto.get_images_by_subcategory(sub_category_id)
        serializer = ActivityPhotosSerializer(photos,many=True)

        return Response(
            data={'photos': serializer.data},
            status=status.HTTP_200_OK)


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


class ActivitiesSearchView(APIView):
    def get(self, request, **kwargs):
        q = request.query_params.get('q')
        search = ActivitySearchEngine()
        filters = search.filter_query(request.query_params)
        # excludes = search.exclude_query(request.query_params)

        query = search.get_query(q, ['title', 'short_description', 'content', \
                                     'tags__name','organizer__name'])
        if query:
            activities = Activity.objects.filter(query)
        else:
            activities = Activity.objects.all()

        activities = activities.filter(filters)\
            .annotate(number_assistants=Count('chronograms__orders__assistants'))\
            .order_by('number_assistants', 'chronograms__initial_date')
            # .order_by('score', 'number_assistants', 'chronograms__initial_date')

        serializer = ActivitiesSerializer(activities, many=True)
        result = serializer.data
        return Response(result)
