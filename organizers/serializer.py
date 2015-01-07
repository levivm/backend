from .models import Organizer
from .models import Instructor

from rest_framework import serializers

class OrganizersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organizer
		fields = (
			'user',
			'name',
			'website',
			'photo'
			)

class InstructorsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Instructor
		fields = (
			'full_name',
			'organizer'
			)