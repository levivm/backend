from .model import Activity
from rest_framework import serializers

class ActivitiesSerializer(serializers.ModelSerializer):
	class Meta:
		model = Activity
		fields = (
			'id',
			'type',
			'title',
			'short_description'
			)