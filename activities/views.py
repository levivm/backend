# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.db.models.aggregates import Count
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, ListAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from activities.mixins import CalculateActivityScoreMixin, ListUniqueOrderedElementsMixin
from activities.permissions import IsActivityOwnerOrReadOnly
from activities.searchs import ActivitySearchEngine
from activities.tasks import SendEmailCalendarTask, SendEmailLocationTask, SendEmailShareActivityTask
from locations.serializers import LocationsSerializer
from organizers.models import Organizer
from utils.paginations import MediumResultsSetPagination
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly
from .models import Activity, Category, SubCategory, Tags, Calendar, ActivityPhoto, \
    ActivityStockPhoto
from .permissions import IsActivityOwner
from .serializers import ActivitiesSerializer, CategoriesSerializer, SubCategoriesSerializer, \
    TagsSerializer, CalendarSerializer, ActivityPhotosSerializer, ActivitiesCardSerializer


class CalendarViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer
    lookup_url_kwarg = 'calendar_pk'
    model = Calendar
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwnerOrReadOnly)

    def get_queryset(self):
        activity_id = self.kwargs.get('activity_pk', None)
        activity = get_object_or_404(Activity, pk=activity_id)
        return activity.calendars.all()

    def list(self, request, *args, **kwargs):
        calendars = self.get_queryset().order_by('initial_date')
        if request.GET.get('actives'):
            calendars = calendars.filter(initial_date__gt=now())

        calendar_serializer = self.serializer_class(calendars, many=True)
        return Response(calendar_serializer.data)

    def destroy(self, request, *args, **kwargs):
        calendar = self.get_object()
        if calendar.orders.count() == 0:
            return super().destroy(request, *args, **kwargs)

        return Response({'detail': _('No puede eliminar este calendario, \
                            tiene estudiantes inscritos, contactanos.')},
                        status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        result = super().update(request, *args, **kwargs)
        calendar = self.get_object()
        task = SendEmailCalendarTask()
        task.apply_async((calendar.id,), countdown=1800)
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
            'price_range': settings.PRICE_RANGE
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
        return activity.pictures.all()

    def create(self, request, *args, **kwargs):
        activity = self.get_activity_object(**kwargs)
        # is_stock_image = request.data.get('is_stock_image',False)

        serializer = ActivityPhotosSerializer(data=request.data,
                                              context={'activity': activity,
                                                       'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        self.calculate_score(activity_id=activity.id)
        headers = self.get_success_headers(serializer.data)
        activity_serializer = self.get_activity_serializer(instance=activity,
                                                           context={'request': request})
        return Response(
                data={'activity': activity_serializer.data, 'picture': serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers)

    def set_cover_from_stock(self, request, *args, **kwargs):
        activity = self.get_activity_object(**kwargs)
        cover_id = request.data.get('cover_id')
        stock_cover_picture = get_object_or_404(ActivityStockPhoto, pk=cover_id)
        photo = ActivityPhoto.create_from_stock(stock_cover_picture, activity)

        serializer = ActivityPhotosSerializer(instance=photo)

        # self.calculate_score(activity_id=activity.id)
        headers = self.get_success_headers(serializer.data)
        activity_serializer = self.get_activity_serializer(instance=activity,
                                                           context={'request': request})
        return Response(
                data={'activity': activity_serializer.data, 'picture': serializer.data},
                status=status.HTTP_201_CREATED,
                headers=headers)

    def destroy(self, request, *args, **kwargs):
        gallery_pk = kwargs.get('gallery_pk')
        activity = self.get_activity_object(**kwargs)
        activity_serializer = self.get_activity_serializer(instance=activity,
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
    lookup_url_kwarg = 'subcategory_id'

    def get_pool_from_stock(self, request, *args, **kwargs):
        sub_category = self.get_object()
        pictures = ActivityStockPhoto.get_images_by_subcategory(sub_category)
        serializer = ActivityPhotosSerializer(pictures, many=True)

        return Response(
                data={'pictures': serializer.data},
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


class ActivitiesSearchView(ListUniqueOrderedElementsMixin, ListAPIView):
    serializer_class = ActivitiesCardSerializer
    pagination_class = MediumResultsSetPagination

    def list(self, request, **kwargs):
        q = request.query_params.get('q')
        search = ActivitySearchEngine()
        filters = search.filter_query(request.query_params)
        # excludes = search.exclude_query(request.query_params)

        query = search.get_query(q, ['title', 'short_description', 'content',
                                     'tags__name', 'organizer__name'])
        if query:
            activities = Activity.objects.select_related('location') \
                .select_related('organizer').filter(query)
        else:
            activities = Activity.objects.select_related('location') \
                .select_related('organizer')

        activities = activities.filter(filters) \
            .annotate(number_assistants=Count('calendars__orders__assistants')) \
            .order_by('number_assistants', 'calendars__initial_date')
        # .order_by('score', 'number_assistants', 'calendars__initial_date')

        # serializer = ActivitiesCardSerializer(activities, many=True)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(self.unique_everseen(page, lambda p: p), many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(self.unique_everseen(activities,
                                                                   lambda activity: activity.id), many=True)
        result = serializer.data
        return Response(result)


class ShareActivityEmailView(APIView):
    """
    View to share an activity by email
    """
    email_validator = EmailValidator()

    def get_activity(self):
        return get_object_or_404(Activity, id=self.kwargs.get('activity_pk'))

    def post(self, request, *args, **kwargs):
        activity = self.get_activity()
        emails = request.data.get('emails')

        if not emails:
            raise ValidationError(_('Se necesita al menos un correo para enviar'))

        emails = [email.strip() for email in emails.split(',')]
        for email in emails:
            try:
                self.email_validator(email)
            except DjangoValidationError:
                return Response(_('Introduzca una dirección de correo electrónico válida'),
                                status=status.HTTP_400_BAD_REQUEST)

        task = SendEmailShareActivityTask()
        task.delay(request.user.id, activity.id, emails=emails, message=request.data.get('message'))

        return Response('OK')


class AutoCompleteView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        result = []

        if query:
            activities = self.get_list(Activity.objects.filter(title__istartswith=query), 'title')
            tags = self.get_list(Tags.objects.filter(name__istartswith=query), 'name')
            categories = self.get_list(Category.objects.filter(name__istartswith=query), 'name')
            subcategories = self.get_list(SubCategory.objects.filter(name__istartswith=query), 'name')
            organizers = self.get_list(Organizer.objects.filter(name__istartswith=query), 'name')
            result = [*activities, *tags, *categories, *subcategories, *organizers]

        return Response(list(set(result)))

    def get_list(self, queryset, attr):
        return queryset.only(attr).values_list(attr, flat=True)
