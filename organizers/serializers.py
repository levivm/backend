from utils.serializers import UnixEpochDateField
from .models import Organizer
from .models import Instructor
from users.forms import UserCreateForm
from users.serializers import UserSerializer
from rest_framework import serializers

class OrganizersSerializer(serializers.ModelSerializer):

    user_type = serializers.SerializerMethodField()
    user = UserSerializer()
    created_at = serializers.SerializerMethodField()

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
            )
        read_only_fields = ('id','photo',)
        depth = 1

    def get_user_type(self,obj):
        return UserCreateForm.USER_TYPES[0][0]

    def get_created_at(self, obj):
        return UnixEpochDateField().to_representation(obj.created_at)


class InstructorsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instructor
        fields = (
            'full_name',
            'organizer'
            )