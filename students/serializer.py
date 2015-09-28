from rest_framework import serializers

from .models import Student
from users.serializers import UsersSerializer
from users.forms import UserCreateForm
from utils.mixins import FileUploadMixin
from utils.serializers import UnixEpochDateField


class StudentsSerializer(FileUploadMixin, serializers.ModelSerializer):
    user = UsersSerializer()
    user_type = serializers.SerializerMethodField()
    birth_date = UnixEpochDateField()
    referrer_code = serializers.CharField(read_only=True)

    class Meta:
        model = Student
        fields = (
            'id',
            'photo',
            'user',
            'gender',
            'user',
            'user_type',
            'birth_date',
            'city',
            'referrer_code',
        )

    def validate_photo(self, file):
        return self.clean_file(file)

    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[1][0]

    def update(self, instance, validated_data):
        instance.update(validated_data)
        instance.update_base_info(validated_data['user'])
        return instance
