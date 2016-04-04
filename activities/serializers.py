# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

import urllib

from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from activities.mixins import WishListSerializerMixin
from activities.models import Activity, Category, SubCategory, Tags, Calendar, \
    CalendarSession, ActivityPhoto
from locations.serializers import LocationsSerializer
from orders.serializers import AssistantsSerializer
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer, InstructorsSerializer
from students.models import Student, WishList
from reviews.serializers import ReviewSerializer
from utils.mixins import FileUploadMixin
from utils.serializers import UnixEpochDateField, RemovableSerializerFieldMixin

class TagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = (
            'name',
        )


class SubCategoriesSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='id',
    )

    class Meta:
        model = SubCategory
        fields = (
            'name',
            'id',
            'category'
        )
        depth = 1


class CategoriesSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    subcategories = SubCategoriesSerializer(many=True, read_only=True, source='subcategory_set')
    icon_default = serializers.SerializerMethodField()
    icon_active = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            'name',
            'id',
            'subcategories',
            'color',
            'icon_default',
            'icon_active',
            'cover'
        )

    def get_icon_default(self, obj):
        url = settings.STATIC_IMAGES_URL
        file_name = "icon_category_%s_default.png" % obj.name.lower()
        return "%s%s" % (url, file_name)

    def get_icon_active(self, obj):
        url = settings.STATIC_IMAGES_URL
        file_name = "icon_category_%s_active.png" % obj.name.lower()
        return "%s%s" % (url, file_name)

    def get_cover(self, obj):
        url = '/css/img/categories/'
        file_name = "%s.jpg" % obj.name.lower()
        file_name = urllib.parse.quote(file_name)
        return "%s%s" % (url, file_name)


class ActivityPhotosSerializer(FileUploadMixin, serializers.ModelSerializer):
    class Meta:
        model = ActivityPhoto
        fields = (
            'photo',
            'main_photo',
            'id',
        )

    def validate(self, data):
        activity = self.context['activity']
        photos_count = activity.pictures.count()

        if photos_count >= settings.MAX_ACTIVITY_PHOTOS:
            msg = _(u'Ya excedió el número máximo de imágenes por actividad.')
            raise serializers.ValidationError(msg)

        data['activity'] = activity

        return data

    def validate_photo(self, file):
        is_stock_image = self.context['request'].data.get('is_stock_image')
        if not is_stock_image:
            return file

        return self.clean_file(file)

    def create(self, validated_data):
        is_main_photo = validated_data['main_photo']
        if is_main_photo:
            activity = validated_data['activity']
            ActivityPhoto.objects.filter(activity=activity, main_photo=True).delete()

        photo = super(ActivityPhotosSerializer, self).create(validated_data)

        return photo


class CalendarSessionSerializer(serializers.ModelSerializer):
    date = UnixEpochDateField()
    start_time = UnixEpochDateField()
    end_time = UnixEpochDateField()

    class Meta:
        model = CalendarSession
        fields = (
            'id',
            'date',
            'start_time',
            'end_time',
        )


class CalendarSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    sessions = CalendarSessionSerializer(many=True)
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
    initial_date = UnixEpochDateField()
    closing_sale = UnixEpochDateField()
    assistants = serializers.SerializerMethodField()
    available_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Calendar
        fields = (
            'id',
            'activity',
            'initial_date',
            'closing_sale',
            'number_of_sessions',
            'session_price',
            'capacity',
            'sessions',
            'assistants',
            'is_weekend',
            'duration',
            'is_free',
            'available_capacity',
        )
        depth = 1

    def get_assistants(self, obj):
        assistants = obj.get_assistants()
        assistants_serialzer = AssistantsSerializer(assistants, many=True, context=self.context,
                                                    remove_fields=['lastest_refund', 'student'])
        return assistants_serialzer.data

    def get_available_capacity(self, obj):
        return obj.available_capacity()

    def validate_activity(self, value):
        return value

    def validate_schedules(self, value):
        return value

    def validate_initial_date(self, value):
        return value

    def validate_sessions(self, value):
        if len(value) > 0:
            return value
        raise serializers.ValidationError(_("Deber haber mínimo una sesión."))

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(_("La capacidad no puede ser negativa."))
        return value

    def validate_number_of_sessions(self, value):
        if value < 1:
            raise serializers.ValidationError(_(u"Debe especificar por lo menos una sesión"))
        return value

    def _validate_session_price(self, data):
        value = data.get('session_price')
        if value < 1:
            error = {'session_price': _("Introduzca un monto valido")}
            raise serializers.ValidationError(error)

        if value < settings.MIN_ALLOWED_CALENDAR_PRICE:
            msg = _("El precio no puede ser menor de {:d}"
                    .format(settings.MIN_ALLOWED_CALENDAR_PRICE))
            error = {'session_price': msg}
            raise serializers.ValidationError(error)

    def _set_initial_date(self, data):
        sessions = data.get('sessions')
        first_session = (sessions[:1] or [None])[0]
        data['initial_date'] = first_session.get('date')
        return data

    def _validate_session(self, sessions_amount, index, session):

        start_time = session['start_time']
        end_time = session['end_time']
        if start_time >= end_time:
            msg = _(u"La hora de inicio debe ser menor a la hora final")
            errors = [{}] * sessions_amount
            errors[index] = {'start_time_' + str(index): [msg]}
            raise serializers.ValidationError({'sessions': errors})

    def _proccess_sessions(self, data):

        sessions_data = data['sessions']
        data['is_weekend'] = True

        sessions_amount = len(sessions_data)
        if not sessions_amount:
            raise serializers.ValidationError(_(u"Debe especificar por lo menos una sesión"))

        for i in range(sessions_amount):

            session = sessions_data[i]
            n_session = sessions_data[i + 1] if i + 1 < sessions_amount else None

            self._validate_session(sessions_amount, i, session)

            date = session['date'].date()

            weekday = date.weekday()
            if weekday < 5:
                data['is_weekend'] = False

            if not n_session:
                continue

            n_date = n_session['date'].date()

            if date > n_date:
                msg = _(u'La fecha su sesión debe ser mayor a la anterior')
                errors = [{}] * sessions_amount
                errors[i + 1] = {'date_' + str(0): [msg]}
                raise serializers.ValidationError({'sessions': errors})

            elif date == n_date:
                if session['end_time'].time() > n_session['start_time'].time():
                    msg = _(
                        u'La hora de inicio de su sesión debe ser después de la sesión anterior')
                    errors = [{}] * sessions_amount
                    errors[i + 1] = {'start_time_' + str(i + 1): [msg]}
                    raise serializers.ValidationError({'sessions': errors})

        return data

    def validate(self, data):

        is_free = data.get('is_free')
        if not is_free:
            self._validate_session_price(data)

        data = self._set_initial_date(data)
        data = self._proccess_sessions(data)
        initial_date = data['initial_date']
        closing_sale = data['closing_sale']
        if initial_date < closing_sale:
            raise serializers.ValidationError(
                {'closing_sale': _("La fecha de cierre de ventas no puede ser mayor \
                                        a la fecha de inicio.")})

        return data

    def create(self, validated_data):
        sessions_data = validated_data.get('sessions')
        last_session = sessions_data[-1]
        del (validated_data['sessions'])
        calendar = Calendar.objects.create(**validated_data)
        calendar.activity.set_last_date(last_session)
        _sessions = [CalendarSession(calendar=calendar, **data) for data in sessions_data]
        CalendarSession.objects.bulk_create(_sessions)

        return calendar

    def update(self, instance, validated_data):
        sessions_data = validated_data.get('sessions')
        last_session = sessions_data[-1]
        instance.activity.set_last_date(last_session)
        del (validated_data['sessions'])
        instance.update(validated_data)
        sessions = instance.sessions.all()
        sessions.delete()

        _sessions = [CalendarSession(calendar=instance, **data) for data in sessions_data]
        CalendarSession.objects.bulk_create(_sessions)

        return instance

class ActivitiesAutocompleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
        )


class ActivitiesCardSerializer(WishListSerializerMixin, serializers.ModelSerializer):
    closest_calendar = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    pictures = serializers.SerializerMethodField()
    organizer = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'category',
            'sub_category',
            'pictures',
            'organizer',
            'published',
            'closest_calendar',
            'organizer',
            'wish_list',
        )

    def get_category(self, obj):
        return CategoriesSerializer(instance=obj.sub_category.category,
                                    remove_fields=['subcategories']).data

    def get_closest_calendar(self, obj):
        request = self.context.get('request')
        if not request:
            instance = obj.closest_calendar()
        else:
            cost_start = request.query_params.get('cost_start')
            cost_end = request.query_params.get('cost_end')
            initial_date = request.query_params.get('date')
            instance = obj.closest_calendar(initial_date, cost_start, cost_end)
        return CalendarSerializer(instance,
                                  remove_fields=['sessions', 'assistants', 'activity',
                                                 'number_of_sessions', 'capacity',
                                                 'available_capacity', 'is_weekend']).data

    def get_pictures(self, obj):
        pictures = [p for p in obj.pictures.all() if p.main_photo]
        return ActivityPhotosSerializer(pictures, many=True).data

    def get_organizer(self, obj):
        return OrganizersSerializer(obj.organizer,
                                    remove_fields=['bio', 'headline', 'website',
                                                   'youtube_video_url', 'telephone',
                                                   'instructors', 'locations', 'user', 'user_type',
                                                   'created_at']).data


class ActivitiesSerializer(WishListSerializerMixin, serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    sub_category = serializers.SlugRelatedField(slug_field='id',
                                                queryset=SubCategory.objects.all(), required=True)
    category = serializers.SerializerMethodField()
    location = LocationsSerializer(read_only=True)
    pictures = ActivityPhotosSerializer(read_only=True, many=True)
    calendars = CalendarSerializer(read_only=True, many=True)
    last_date = serializers.SerializerMethodField()
    organizer = OrganizersSerializer(read_only=True)
    sub_category_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True, required=False)
    required_steps = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    closest_calendar = CalendarSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = (
            'id',
            'title',
            'short_description',
            'sub_category',
            'sub_category_display',
            'level',
            'level_display',
            'tags',
            'category',
            'content',
            'requirements',
            'return_policy',
            'extra_info',
            'audience',
            'goals',
            'methodology',
            'location',
            'pictures',
            'youtube_video_url',
            'published',
            'certification',
            'last_date',
            'calendars',
            'closest_calendar',
            'required_steps',
            'steps',
            'organizer',
            'instructors',
            'score',
            'rating',
            'wish_list',
            'reviews'
        )
        depth = 1

    def get_required_steps(self, obj):
        if not obj.pictures.count():
            return settings.PREVIOUS_FIST_PUBLISH_REQUIRED_STEPS

        return settings.REQUIRED_STEPS

    def get_steps(self, obj):
        return settings.ACTIVITY_STEPS

    def get_last_date(self, obj):
        return UnixEpochDateField().to_representation(obj.last_date)

    def get_sub_category_display(self, obj):
        return obj.sub_category.name

    def get_category(self, obj):
        return CategoriesSerializer(instance=obj.sub_category.category,
                                    remove_fields=['subcategories']).data

    def get_category_display(self, obj):
        return obj.sub_category.category.name

    def get_level_display(self, obj):
        return obj.get_level_display()

    def get_reviews(self,obj):
        show_reviews = self.context.get('show_reviews')
        request = self.context.get('request')
        if show_reviews and request:
            reviews = obj.reviews.filter(author__user=request.user)
            return ReviewSerializer(reviews, many=True).data
        return []

    def validate(self, data):
        request = self.context['request']
        user = request.user
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError(_("Usuario no es organizador"))

        data['organizer'] = organizer

        return data

    def create(self, validated_data):
        request = self.context['request']
        tags = request.data.get('tags')

        if 'category' in validated_data:
            del validated_data['category']
        activity = Activity.objects.create(**validated_data)
        activity.update_tags(tags)

        return activity

    def update(self, instance, validated_data):
        request = self.context['request']
        tags = request.data.get('tags')
        instance.update(validated_data)
        instance.update_tags(tags)

        return instance
