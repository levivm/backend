from .model import Activity
from rest_framework import serializers

class StudentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = (
			'user',
			'gender'
			)

class AssistantSerializer(serializers.ModelSerializer):
	class Meta:
		model = Assistant
		fields = (
			'first_name',
			'last_name',
			'email'
			)

