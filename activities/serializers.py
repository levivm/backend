# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

from activities.models import Activity, Category, SubCategory, Tags, Chronogram, Session, ActivityPhoto
from locations.serializers import LocationsSerializer
from orders.serializers import AssistantSerializer
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer, InstructorsSerializer
from utils.mixins import AssignPermissionsMixin, FileUploadMixin
from utils.serializers import UnixEpochDateField


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


class CategoriesSerializer(serializers.ModelSerializer):
    subcategories = SubCategoriesSerializer(many=True, read_only=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = (
            'name',
            'id',
            'subcategories'
        )


class ActivityPhotosSerializer(AssignPermissionsMixin, FileUploadMixin, serializers.ModelSerializer):
    permissions = ('activities.delete_activityphoto', )

    class Meta:
        model = ActivityPhoto
        fields = (
            'photo',
            'main_photo',
            'id',
        )

    def validate(self, data):
        activity = self.context['activity']
        photos_count = activity.photos.count()

        if photos_count >= settings.MAX_ACTIVITY_PHOTOS:
            msg = _(u'Ya excedió el número máximo de imágenes por actividad.')
            raise serializers.ValidationError(msg)

        data['activity'] = activity

        return data

    def validate_photo(self, file):
        return self.clean_file(file)

    def create(self, validated_data):
        is_main_photo = activity = validated_data['main_photo']
        if is_main_photo:
            activity = validated_data['activity']
            ActivityPhoto.objects.filter(activity=activity, main_photo=True).delete()

        photo = super(ActivityPhotosSerializer, self).create(validated_data)

        request = self.context['request']
        self.assign_permissions(request.user, photo)
        return photo


class SessionsSerializer(serializers.ModelSerializer):
    date = UnixEpochDateField()
    start_time = UnixEpochDateField()
    end_time = UnixEpochDateField()

    class Meta:
        model = Session
        fields = (
            'id',
            'date',
            'start_time',
            'end_time',
        )

    def validate(self, data):
        start_time = data['start_time']
        end_time = data['end_time']

        if start_time >= end_time:
            raise serializers.ValidationError(_("La hora de inicio debe ser menor a la hora final"))
        return data


class ChronogramsSerializer(AssignPermissionsMixin, serializers.ModelSerializer):
    sessions = SessionsSerializer(many=True)
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())
    initial_date = UnixEpochDateField()
    closing_sale = UnixEpochDateField()
    assistants = serializers.SerializerMethodField()
    permissions = ('activities.change_chronogram', 'activities.delete_chronogram')

    class Meta:
        model = Chronogram
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
        )
        depth = 1

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

    def validate_session_price(self, value):
        if value < 1:
            raise serializers.ValidationError(_("El precio no puede ser negativo."))
        return value

    def validate_capacity(self, value):
        if value < 1:
            raise serializers.ValidationError(_("La capacidad no puede ser negativa."))
        return value

    def validate_number_of_sessions(self, value):
        if value < 1:
            raise serializers.ValidationError(_(u"Debe especificar por lo menos una sesión"))
        return value

    def _valid_sessions(self, data):

        session_data = data['sessions']
        initial_date = data['initial_date']

        f_range = len(session_data)
        for i in range(f_range):

            session = session_data[i]
            n_session = session_data[i + 1] if i + 1 < f_range else None

            date = session['date'].date()

            if date < initial_date.date():
                msg = _(u'La sesión no puede empezar antes de la fecha de inicio')
                errors    = [{}]*f_range
                errors[i] = {'date_'+str(0):[msg]} 
                raise serializers.ValidationError({'sessions':errors})

            if not n_session:
                continue

            n_date = n_session['date'].date()

            if date > n_date:
                msg = _(u'La fecha su sesión debe ser mayor a la anterior')
                errors    = [{}]*f_range
                errors[i+1] = {'date_'+str(0):[msg]} 
                raise serializers.ValidationError({'sessions':errors})

                raise serializers.ValidationError({'sessions_' + str(i + 1): _(msg)})
            elif date == n_date:
                if session['end_time'].time() > n_session['start_time'].time():
                    msg = _(u'La hora de inicio de su sesión debe ser después de la sesión anterior')
                    errors    = [{}]*f_range
                    errors[i+1] = {'start_time_'+str(1):[msg]} 
                    raise serializers.ValidationError({'sessions':errors})

    def validate(self, data):
        initial_date = data['initial_date']
        closing_sale = data['closing_sale']
        if initial_date > closing_sale:
            raise serializers.ValidationError(_("La fecha de cierre debe ser mayor a la fecha de inicio."))

        self._valid_sessions(data)

        return data

    def create(self, validated_data):
        sessions_data = validated_data.get('sessions')
        del (validated_data['sessions'])
        chronogram = Chronogram.objects.create(**validated_data)
        _sessions = [Session(chronogram=chronogram, **data) for data in sessions_data]
        Session.objects.bulk_create(_sessions)

        request = self.context['request']
        self.assign_permissions(request.user, chronogram)

        return chronogram

    def update(self, instance, validated_data):
        sessions_data = validated_data.get('sessions')
        del (validated_data['sessions'])
        instance.update(validated_data)
        sessions = instance.sessions.all()
        sessions.delete()

        _sessions = [Session(chronogram=instance, **data) for data in sessions_data]
        sessions = Session.objects.bulk_create(_sessions)

        return instance

    def get_assistants(self, obj):
        assistants = []
        orders = obj.orders.all()

        for order in orders:
            assistants.append(order.assistants.all())

        assistants = [item for sublist in assistants for item in sublist]
        assistants_serialzer = AssistantSerializer(assistants, many=True)
        return assistants_serialzer.data


class ActivitiesSerializer(AssignPermissionsMixin, serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(many=True, slug_field='name', read_only=True)
    sub_category = serializers.SlugRelatedField(slug_field='id', queryset=SubCategory.objects.all(), required=True)
    category = serializers.CharField(write_only=True, required=True)
    category_id = serializers.SlugRelatedField(source='sub_category.category', read_only=True, slug_field='id')
    location = LocationsSerializer(read_only=True)
    photos = ActivityPhotosSerializer(read_only=True, many=True)
    chronograms = ChronogramsSerializer(read_only=True, many=True)
    last_date = serializers.SerializerMethodField()
    organizer = OrganizersSerializer(read_only=True)
    category_display = serializers.SerializerMethodField()
    sub_category_display = serializers.SerializerMethodField()
    level_display = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True, required=False)
    required_steps = serializers.SerializerMethodField()
    steps = serializers.SerializerMethodField()
    permissions = ('activities.change_activity', )

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
            'category_id',
            'category_display',
            'content',
            'requirements',
            'return_policy',
            'extra_info',
            'audience',
            'goals',
            'methodology',
            'location',
            'photos',
            'youtube_video_url',
            'published',
            'certification',
            'enroll_open',
            'last_date',
            'chronograms',
            'required_steps',
            'steps',
            'organizer',
            'instructors',
        )
        depth = 1


    def get_required_steps(self,obj):
        if not obj.photos.count():
            return settings.PREVIOUS_FIST_PUBLISH_REQUIRED_STEPS

        return settings.REQUIRED_STEPS

    def get_steps(self,obj):
        return settings.ACTIVITY_STEPS


    def get_last_date(self, obj):
        return UnixEpochDateField().to_representation(obj.last_sale_date())


    def get_sub_category_display(self, obj):
        return obj.sub_category.name

    def get_category_display(self, obj):
        return obj.sub_category.category.name


    def get_level_display(self, obj):
        return obj.get_level_display()


    def validate(self, data):

        request = self.context['request']
        user = request.user
        organizer = None
        try:
            organizer = Organizer.objects.get(user=user)
        except Organizer.DoesNotExist:
            raise serializers.ValidationError("Usuario no es organizador")

        data['organizer'] = organizer

        return data

    def create(self, validated_data):
        request = self.context['request']
        _tags = request.DATA.get('tags')

        tags = Tags.update_or_create(_tags)
        if 'category' in validated_data:
            del validated_data['category']
        activity = Activity.objects.create(**validated_data)
        activity.tags.clear()
        activity.tags.add(*tags)

        self.assign_permissions(request.user, activity)
        return activity

    def update(self, instance, validated_data):
        request = self.context['request']
        organizer = validated_data.get('organizer')
        instructors_data = validated_data.get('instructors', [])
        instance.add_instructors(instructors_data, organizer)

        # del (validated_data['location'])
        instance.update(validated_data)


        instance.save()

        _tags = request.DATA.get('tags')
        if _tags:
            tags = Tags.update_or_create(_tags)
            instance.tags.clear()
            instance.tags.add(*tags)

        return instance
