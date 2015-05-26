from .models import Student
from rest_framework import serializers
from users.serializers import UserSerializer


class StudentsSerializer(serializers.ModelSerializer):
	user = UserSerializer()

	class Meta:
		model = Student
		fields = (
            'id',
			'photo',
			'user',
			'gender',
			'user'
			)