from .model import Organizer
from .model import Instructor

from rest_framework import serializers

class OrganizersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organizer
		fields = (
			'user',
			'name',
			'website'
			)

class InstructorsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Instructor
		fields = (
			'full_name',
			'organizer'
			)