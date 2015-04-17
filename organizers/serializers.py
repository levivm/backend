from .models import Organizer
from .models import Instructor
from users.forms import UserCreateForm
from rest_framework import serializers



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


class OrganizersSerializer(serializers.ModelSerializer):

	user_type = serializers.SerializerMethodField()
	instructors = InstructorsSerializer(many=True)
	
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
			'user_type',
			'instructors'
			)
		read_only_fields = ('id','photo',)
		depth = 1


	def get_user_type(self,obj):
		return UserCreateForm.USER_TYPES[0][0]