from rest_framework import serializers
from organizers.models import OrganizerBankInfo
from users.serializers import UsersSerializer
from users.forms import UserCreateForm
from utils.serializers import UnixEpochDateField, RemovableSerializerFieldMixin,\
                              BankField
from .models import Organizer
from .models import Instructor
from locations.serializers import LocationsSerializer
from utils.mixins import FileUploadMixin


class InstructorsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    organizer = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Instructor
        fields = (
            'full_name',
            'id',
            'bio',
            'organizer',
            'website',
        )

    def create(self, validated_data):
        organizer = self.context['request'].user.organizer_profile
        validated_data.update({ 'organizer': organizer })
        return super(InstructorsSerializer, self).create(validated_data)


class OrganizersSerializer(RemovableSerializerFieldMixin, FileUploadMixin, serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    user = UsersSerializer(read_only=True)
    created_at = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True, read_only=True)
    locations = serializers.SerializerMethodField()
    verified_email = serializers.BooleanField(read_only=True)

    class Meta:
        model = Organizer
        fields = (
            'id',
            'user',
            'name',
            'bio',
            'headline',
            'website',
            'youtube_video_url',
            'telephone',
            'photo',
            'user_type',
            'created_at',
            'instructors',
            'locations',
            'rating',
            'verified_email',
            'type',
        )
        read_only_fields = ('id',)
        depth = 1

    def validate_photo(self, file):
        return self.clean_file(file)

    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[0][0]

    def get_created_at(self, obj):
        return UnixEpochDateField().to_representation(obj.created_at)

    def get_locations(self, obj):
        locations = obj.locations.all()
        if not locations:
            activity = obj.activity_set.last()
            locations = [activity.location] if activity else []
        return LocationsSerializer(locations, many=True).data


class OrganizerBankInfoSerializer(serializers.ModelSerializer):

    bank = BankField(choices=OrganizerBankInfo.BANKS)


    class Meta:
        model = OrganizerBankInfo


    def validate(self, validated_data):
        person_type = validated_data.get('person_type')
        if person_type ==  OrganizerBankInfo.JURIDICAL:
            required_fields = ['fiscal_address', 'billing_telephone', 'regimen']
            missing_fields = [field for field in required_fields if not validated_data.get(field)]
            first_missing_field, *_ = missing_fields if missing_fields else [None, None]
            if first_missing_field:
                raise serializers.ValidationError({first_missing_field: 'Este campo es requerido.'})

        return validated_data