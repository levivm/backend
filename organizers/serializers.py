from .models import Organizer
from .models import Instructor
from users.forms import UserCreateForm
from rest_framework import serializers

class OrganizersSerializer(serializers.ModelSerializer):

	user_type = serializers.SerializerMethodField()
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
			'photo',
			'user_type'
			)
		read_only_fields = ('id','photo',)
		depth = 1


	def get_user_type(self,obj):
		return UserCreateForm.USER_TYPES[0][0]

class InstructorsSerializer(serializers.ModelSerializer):

	id = serializers.IntegerField()
	class Meta:
		model = Instructor
		fields = (
			'full_name',
			'id',
			'bio',
			'organizer',
			'photo',
			'website',
			)

	def validate(self,validated_data):
		return validated_data