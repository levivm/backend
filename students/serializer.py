from .models import Student
from rest_framework import serializers
from users.serializers import UserSerializer


class StudentsSerializer(serializers.ModelSerializer):
	user = UserSerializer()
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


    def get_user_type(self, obj):
        return UserCreateForm.USER_TYPES[1][0]