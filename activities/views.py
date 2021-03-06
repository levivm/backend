# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
from itertools import chain

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import EmailValidator
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from rest_framework import viewsets, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404, ListAPIView, RetrieveAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from activities import constants as activities_constants
from activities.mixins import ActivityMixin, \
    ActivityCardMixin, MongoMixin
from activities.permissions import IsActivityOwnerOrReadOnly
from activities.searchs import ActivitySearchEngine
from activities.tasks import SendEmailCalendarTask, \
    SendEmailShareActivityTask, ActivityViewsCounterTask, SendEmailSignUpLeadCouponTask
from activities.utils import ActivityStatsUtil
from authentication.permissions import IsNotAuthenticated
from locations.serializers import LocationsSerializer
from orders.models import Order
from organizers.models import Organizer
from utils.paginations import SmallResultsSetPagination
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly, IsOrganizer
from .models import Activity, Category, SubCategory, Tags, Calendar, ActivityPhoto, \
    ActivityStockPhoto, CalendarPackage
from .permissions import IsActivityOwner
from .serializers import ActivitiesSerializer, CategoriesSerializer, SubCategoriesSerializer,\
    TagsSerializer, CalendarSerializer, ActivityPhotosSerializer, ActivitiesCardSerializer,\
    ActivityStockPhotosSerializer


class CalendarViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer
    lookup_url_kwarg = 'calendar_pk'
    model = Calendar
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwnerOrReadOnly)

    def get_queryset(self):
        activity_id = self.kwargs.get('activity_pk', None)
        activity = get_object_or_404(Activity, pk=activity_id)
        return activity.calendars.all()

    def perform_update(self, serializer):
        calendar = self.get_object()

        old_initial_date = calendar.initial_date
        new_initial_date = serializer.validated_data.get('initial_date').date()

        serializer.save()

        # If the initial date changed, send an email to students
        if not old_initial_date == new_initial_date:
            task = SendEmailCalendarTask()
            task.apply_async((calendar.id,), countdown=1800)

    def list(self, request, *args, **kwargs):
        calendars = self.get_queryset().order_by('initial_date')
        if request.GET.get('actives'):
            calendars = calendars.filter(initial_date__gt=now())

        calendar_serializer = self.serializer_class(calendars, many=True)
        return Response(calendar_serializer.data)

    def destroy(self, request, *args, **kwargs):
        calendar = self.get_object()

        if not calendar.orders.count() == 0:
            return Response({'detail': _('No puede eliminar este calendario, \
                            tiene estudiantes inscritos, contactanos.')},
                            status=status.HTTP_400_BAD_REQUEST)

        if calendar.activity.published and calendar.activity.calendars.count() < 2:
            return Response({'detail': _('No puede eliminar este calendario, \
                            primero debe desactivar la actividad.')},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)


class ActivitiesViewSet(ActivityMixin, viewsets.ModelViewSet):
    serializer_class = ActivitiesSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwnerOrReadOnly)
    lookup_url_kwarg = 'activity_pk'

    def get_queryset(self):
        return Activity.objects.prefetch_related(*self.prefetch_related_fields) \
            .select_related(*self.select_related_fields).all()

    def partial_update(self, request, *args, **kwargs):
        response = super(ActivitiesViewSet, self).partial_update(request, *args, **kwargs)
        self.calculate_score(kwargs[self.lookup_url_kwarg])
        return response

    def destroy(self, request, *args, **kwargs):
        activity = self.get_object()
        if activity.calendars.filter(orders__isnull=False).exists():
            return Response({'detail': _('No puede eliminar esta actividad, \
                            tiene estudiantes inscritos, contactanos.')},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().destroy(request, *args, **kwargs)

    def set_location(self, request, *args, **kwargs):
        activity = self.get_object()

        if activity.calendars.filter(
                orders__status=Order.ORDER_APPROVED_STATUS).count() > 0:
            raise ValidationError({'location': ['No se puede cambiar la ubicación con personas '
                                                'inscritas.']})

        location_data = request.data.copy()
        location_serializer = LocationsSerializer(data=location_data)

        if location_serializer.is_valid(raise_exception=True):
            location = location_serializer.save()
            activity.set_location(location)

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
            'price_range': settings.PRICE_RANGE,
            'package_options': CalendarPackage.TYPE_CHOICES
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


class ActivityPhotosViewSet(ActivityMixin, viewsets.ModelViewSet):
    model = ActivityPhoto
    serializer_class = ActivityPhotosSerializer
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, IsActivityOwner)
    lookup_url_kwarg = 'gallery_pk'

    def get_queryset(self):
        activity = self.get_activity_object(**self.kwargs)
        return activity.pictures.all()

    def create(self, request, *args, **kwargs):
        activity = self.get_activity_object(**kwargs)

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


class CategoryRetrieveAPIView(RetrieveAPIView):
    serializer_class = CategoriesSerializer
    queryset = Category.objects.all()
    lookup_field = 'slug'

    def get_serializer(self, *args, **kwargs):
        kwargs['remove_fields'] = ['subcategories', 'icon_default', 'icon_active']
        return super(CategoryRetrieveAPIView, self).get_serializer(*args, **kwargs)


class SubCategoriesViewSet(viewsets.ModelViewSet):
    queryset = SubCategory.objects.all()
    serializer_class = SubCategoriesSerializer
    lookup_url_kwarg = 'subcategory_id'

    def get_pool_from_stock(self, request, *args, **kwargs):
        sub_category = self.get_object()
        pictures = ActivityStockPhoto.get_images_by_subcategory(sub_category)
        serializer = ActivityStockPhotosSerializer(pictures, many=True)

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


class ActivitiesSearchView(ActivityCardMixin, ListAPIView):
    serializer_class = ActivitiesCardSerializer
    pagination_class = SmallResultsSetPagination
    queryset = Activity.objects.all()
    search_fields = ['title', 'tags__name', 'organizer__name',
                     'sub_category__name', 'sub_category__category__name']

    def list(self, request, **kwargs):
        query_string = request.query_params.get('q')
        order = request.query_params.get('o')
        search = ActivitySearchEngine(query_params=request.query_params,
                                      query_string=query_string,
                                      search_fields=self.search_fields)
        filters = search.filter_query()
        order_by = search.get_order()
        query = search.get_query()

        activities = Activity.objects.select_related(*self.select_related_fields) \
            .prefetch_related(*self.prefetch_related_fields)

        if query:
            activities = activities.filter(query, filters).distinct()
        else:
            activities = activities.filter(filters).distinct()

        if order in [activities_constants.ORDER_CLOSEST, activities_constants.ORDER_MIN_PRICE,
                     activities_constants.ORDER_MAX_PRICE] or request.query_params.get('is_free') is not None:
            extra_q = search.extra_query()
            activities = activities.extra(**extra_q) if extra_q else activities

        activities = activities.order_by(*order_by)

        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(activities, many=True)
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

        params = {
            'activity_id': activity.id,
            'emails': emails,
            'message': request.data.get('message')
        }

        if not request.user.is_authenticated():
            if request.data.get('user_name') is None:
                raise ValidationError('Se necesita autenticarse o enviar el nombre.')
            else:
                params['user_name'] = request.data.get('user_name')
        else:
            params['user_id'] = request.user.id

        task = SendEmailShareActivityTask()
        task.delay(**params)

        return Response('OK')


class AutoCompleteView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q')
        result = []

        if query:
            activities = self.get_list(Activity.objects.filter(title__istartswith=query), 'title')
            tags = self.get_list(Tags.objects.filter(name__istartswith=query), 'name')
            categories = self.get_list(Category.objects.filter(name__istartswith=query), 'name')
            subcategories = self.get_list(SubCategory.objects.filter(name__istartswith=query),
                                          'name')
            organizers = self.get_list(Organizer.objects.filter(name__istartswith=query), 'name')
            result = chain(activities, tags, categories, subcategories, organizers)

        return Response(list(self.unique_and_capitalize(result)))

    def get_list(self, queryset, attr):
        return queryset.only(attr).values_list(attr, flat=True)

    def unique_and_capitalize(self, iterable):
        seen = set()
        for item in iterable:
            item = item.lower()
            if item not in seen:
                seen.add(item)
                yield item


class ActivityStatsView(RetrieveAPIView):
    permission_classes = (IsAuthenticated, IsOrganizer, IsActivityOwner)
    lookup_url_kwarg = 'activity_pk'
    serializer_class = ActivitiesSerializer

    def get_queryset(self):
        self.profile = self.request.user.organizer_profile
        return self.profile.activity_set.all()

    def retrieve(self, request, *args, **kwargs):
        activity = self.get_object()
        self.validate_params()
        year = int(request.query_params.get('year'))
        month = request.query_params.get('month')
        month = int(month) if month else month
        stats = ActivityStatsUtil(activity=activity, year=year, month=month)
        points = stats.points()

        return Response({
            'created_at': activity.created_at.date().isoformat(),
            'points': points,
            'total_points': stats.total_points,
            'total_views': stats.total_views,
            'total_seats_sold': stats.total_seats_sold,
            'next_data': stats.next_data,
        })

    def validate_params(self):
        if not self.request.query_params.get('year'):
            raise ValidationError({'year': _('Este campo es requerido.')})


class ActivityViewsCounterView(GenericViewSet):
    queryset = Activity.objects.all()
    serializer_class = ActivitiesSerializer

    def put(self, request, *args, **kwargs):
        activity = self.get_object()
        task = ActivityViewsCounterTask()
        task.delay(activity_id=activity.id, user_id=request.user.id)
        return Response('OK')


class ActivityFeatureListView(ListAPIView):
    queryset = Activity.objects.featured()
    serializer_class = ActivitiesCardSerializer


class CategoryLeadCreateView(MongoMixin, GenericAPIView):
    email_validator = EmailValidator()
    permission_classes = [IsNotAuthenticated]
    error = None

    def post(self, request, *args, **kwargs):
        self.validate_data()

        if self.error:
            return Response(self.error, status=status.HTTP_400_BAD_REQUEST)

        leads = self.get_collection(name='leads')
        leads.insert_one(request.data)

        task = SendEmailSignUpLeadCouponTask()
        task.delay(email=request.data['email'])
        return Response(status=status.HTTP_201_CREATED)

    def validate_data(self):
        email = self.request.data.get('email')

        try:
            self.email_validator(email)
        except DjangoValidationError:
            self.error = {'email': [_('Introduzca una dirección de correo electrónico válida')]}

        category = self.request.data.get('category')
        if not Category.objects.filter(id=category).exists():
            self.error = {'category': [_('La categoría seleccionada no existe')]}
