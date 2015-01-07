from .models import Student
from rest_framework import serializers

class StudentsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = (
			'photo',
			'gender',
			'user'
			)