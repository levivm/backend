from rest_framework import serializers
from .models import UserProfile


class UserProfilesSerializer(serializers.ModelSerializer):
	class Meta:
		model = UserProfile
		fields = (
			'bio',
			'id',
			
			)