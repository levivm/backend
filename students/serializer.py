from .models import Student
from rest_framework import serializers
from users.serializers import UserSerializer
from users.forms import UserCreateForm
from utils.mixins import FileUploadMixin




class StudentsSerializer(FileUploadMixin,serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_type = serializers.SerializerMethodField()


    class Meta:
        model = Student
        fields = (
            'id',
            'photo',
            'user',
            'gender',
            'user',
            'user_type',
            )

    def validate_photo(self, file):
        return self.clean_file(file)

    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[1][0]