from .models import Activity
from .serializers import ActivitiesSerializer

from django.htto import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

class ActivitiesList(APIView):

	def get(self, request, format = None):	
		activities = Activity.objects.filter(is_active = True)
		serilized_activities = ActivitiesSerializer(activities, many = True)
		return Response(serilized_activities.data)

class ActivityDetail(APIView):
	def get_object(self, pk):
		try:
			return Game.object.get(pk = pk)
		except Activity.DoesNotExist:
			raise Http404

	def get(self, request, pk, format = None):
		activity = self.get_object(pk):
		serilized_activities = ActivitiesSerializer(activity)
		return Response(serilized_activities.data)


