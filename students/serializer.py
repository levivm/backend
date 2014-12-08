from .model import Student
from rest_framework import serializers

class StudentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = (
			'id',
			'type',
			'title',
			'short_description'
			)