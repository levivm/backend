# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

import urllib
import unicodedata


from django.conf import settings
from django.utils.translation import ugettext as _
from rest_framework import serializers

from activities.mixins import WishListSerializerMixin
from activities.models import Activity, Category, SubCategory, Tags, Calendar, ActivityPhoto, \
    CalendarPackage
from locations.serializers import LocationsSerializer
from orders.serializers import AssistantsSerializer
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer, InstructorsSerializer
from reviews.serializers import ReviewSerializer
from utils.mixins import FileUploadMixin
from utils.serializers import UnixEpochDateField, RemovableSerializerFieldMixin, HTMLField
from . import constants as activities_constants


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
            'category',
            'featured'
        )
        depth = 1


class CategoriesSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    subcategories = SubCategoriesSerializer(many=True, read_only=True, source='subcategory_set')
    icon_default = serializers.SerializerMethodField()
    icon_active = serializers.SerializerMethodField()
    cover = serializers.SerializerMethodField()
    description = HTMLField()

    class Meta:
        model = Category
        fields = (
            'name',
            'id',
            'subcategories',
            'color',
            'icon_default',
            'icon_active',
            'cover',
            'slug',
            'description',
            'cover_photo',
            'content_photo',
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
        file = unicodedata.normalize('NFD', obj.name.lower())
        url = 'static/img/categories/cover/'
        file_name = "%s.jpg" % file
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

        if photos_count >= activities_constants.MAX_ACTIVITY_PHOTOS:
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


class CalendarPackageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(label='ID', read_only=False, required=False)

    class Meta:
        model = CalendarPackage
        fields = (
            'id',
            'quantity',
            'price',
        )

    def validate_quantity(self, quantity):
        if quantity < 1:
            raise serializers.ValidationError(_('La cantidad no puede ser menor a 1.'))

        return quantity

    def validate_price(self, price):
        if price < 30000:
            raise serializers.ValidationError(_('El precio no puede ser menor a 30000.'))

        return price

class CalendarSerializer(RemovableSerializerFieldMixin, serializers.ModelSerializer):
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
    initial_date = UnixEpochDateField()
    assistants = serializers.SerializerMethodField()
    schedules = HTMLField()
    packages = CalendarPackageSerializer(many=True)

    class Meta:
        model = Calendar
        fields = (
            'id',
            'activity',
            'initial_date',
            'enroll_open',
            'session_price',
            'assistants',
            'is_weekend',
            'is_free',
            'available_capacity',
            'note',
            'schedules',
            'packages',
        )
        depth = 1

    def get_assistants(self, obj):
        assistants = obj.get_assistants()
        assistants_serializer = AssistantsSerializer(assistants, many=True, context=self.context,
                                                    remove_fields=['student'])
        return assistants_serializer.data

    def validate_activity(self, value):
        return value

    def validate_schedules(self, value):
        if self.instance:
            if self.instance.orders.available().count() > 0:
                msg = 'No se puede cambiar el horario debido a que existen ordenes relacionadas.'
                raise serializers.ValidationError(_(msg))
        return value

    def validate_initial_date(self, value):
        return value

    def validate_available_capacity(self, value):
        if value < 0:
            raise serializers.ValidationError(_("La capacidad no puede ser negativa."))
        return value

    def _validate_session_price(self, data):
        value = data.get('session_price')
        if value is not None:
            if value < 1:
                error = {'session_price': _("Introduzca un monto valido")}
                raise serializers.ValidationError(error)

            if value < settings.MIN_ALLOWED_CALENDAR_PRICE:
                msg = _("El precio no puede ser menor de {:d}"
                        .format(settings.MIN_ALLOWED_CALENDAR_PRICE))
                error = {'session_price': msg}
                raise serializers.ValidationError(error)

    def validate(self, data):

        is_free = data.get('is_free')
        if not is_free:
            self._validate_session_price(data)

        return data

    def create(self, validated_data):
        packages = validated_data.pop('packages', list())
        calendar = Calendar.objects.create(**validated_data)
        for package in packages:
            CalendarPackage.objects.create(calendar=calendar, **package)
        return calendar

    def update(self, instance, validated_data):
        packages = validated_data.pop('packages', list())
        instance.update(validated_data)

        for package_data in packages:
            id = package_data.pop('id')
            package = instance.packages.get(id=id)
            package.update(package_data)

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
            is_free = request.query_params.get('is_free')
            instance = obj.closest_calendar(initial_date, cost_start, cost_end, is_free)
        return CalendarSerializer(instance,
                                  remove_fields=['assistants', 'activity',
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
    organizer = OrganizersSerializer(read_only=True)
    sub_category_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True, required=False)
    required_steps = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    closest_calendar = CalendarSerializer(read_only=True)
    reviews = serializers.SerializerMethodField()
    wishlist_count = serializers.SerializerMethodField()
    content = HTMLField(allow_blank=True, required=False)
    requirements = HTMLField(allow_blank=True, required=False)
    extra_info = HTMLField(allow_blank=True, required=False)
    audience = HTMLField(allow_blank=True, required=False)
    goals = HTMLField(allow_blank=True, required=False)
    methodology = HTMLField(allow_blank=True, required=False)

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
            'calendars',
            'closest_calendar',
            'required_steps',
            'steps',
            'organizer',
            'instructors',
            'score',
            'rating',
            'wish_list',
            'reviews',
            'wishlist_count',
            'is_open',
        )
        depth = 1

    def get_required_steps(self, obj):
        return activities_constants.REQUIRED_STEPS

    def get_steps(self, obj):
        return activities_constants.ACTIVITY_STEPS

    def get_sub_category_display(self, obj):
        return obj.sub_category.name

    def get_category(self, obj):
        return CategoriesSerializer(instance=obj.sub_category.category,
                                    remove_fields=['subcategories']).data

    def get_category_display(self, obj):
        return obj.sub_category.category.name

    def get_level_display(self, obj):
        return obj.get_level_display()

    def get_reviews(self, obj):
        show_reviews = self.context.get('show_reviews')
        request = self.context.get('request')
        if show_reviews and request:
            reviews = obj.reviews.filter(author__user=request.user)
            return ReviewSerializer(reviews, many=True).data
        return []

    def get_wishlist_count(self, obj):
        return obj.wishlist_count

    def validate(self, data):
        request = self.context['request']
        user = request.user
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError(_("Usuario no es organizador"))

        data['organizer'] = organizer

        return data

    def validate_is_open(self, data):
        if self.instance:
            if self.instance.calendars.count() > 0:
                raise serializers.ValidationError(_("No se puede cambiar el tipo de horario porque"
                                                    " existen calendarios relacionados."))

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
