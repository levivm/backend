from .models import Organizer
from .models import Instructor

from rest_framework import serializers

class OrganizersSerializer(serializers.ModelSerializer):
	class Meta:
		model = Organizer
		fields = (
			'id',
			'user',
			'name',
			'bio',
			'website',
			'youtube_video_url',
			'telephone',
			'photo'
			)
		read_only_fields = ('id','user','photo',)

class InstructorsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Instructor
		fields = (
			'full_name',
			'organizer'
			)