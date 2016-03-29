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
    verified_email = serializers.BooleanField(read_only=True)

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
            'telephone',
            'city',
            'referrer_code',
            'verified_email',
        )

    def validate_photo(self, file):
        return self.clean_file(file)

    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[1][0]

    def validate(self, data):
        user_data = data.get('user')
        if user_data:
            UsersSerializer(data=user_data).is_valid(raise_exception=True)
        return data

    def update(self, instance, validated_data):
        if validated_data.get('user'):
            instance.update_base_info(validated_data.get('user'))
            del(validated_data['user'])
        instance.update(validated_data)
        return instance
