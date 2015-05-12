from rest_framework import serializers

from users.serializers import UserSerializer
from users.forms import UserCreateForm
from utils.serializers import UnixEpochDateField
from .models import Organizer
from .models import Instructor
from locations.serializers import LocationsSerializer


class InstructorsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = Instructor
        fields = (
            'full_name',
            'id',
            'bio',
            'organizer',
            'photo',
            'website',
        )


class OrganizersSerializer(serializers.ModelSerializer):
    user_type = serializers.SerializerMethodField()
    user = UserSerializer()
    created_at = serializers.SerializerMethodField()
    instructors = InstructorsSerializer(many=True)
    locations = LocationsSerializer(many=True)

    class Meta:
        model = Organizer
        fields = (
            'id',
            'user',
            'name',
            'bio',
            'website',
            'youtube_video_url',
            'telephone',
            'photo',
            'user_type',
            'created_at',
            'instructors',
            'locations',
        )
        read_only_fields = ('id', 'photo',)
        depth = 1

    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[0][0]

    def get_created_at(self, obj):
        return UnixEpochDateField().to_representation(obj.created_at)