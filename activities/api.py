from activities.models import Activity
from activities.serializers import ActivitiesSerializer

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response

class ActivitiesList(APIView):

    def get(self, request, format = None):  
        activities = Activity.objects.filter(active = True)
        serilized_activities = ActivitiesSerializer(activities, many = True)
        return Response(serilized_activities.data)

class ActivityDetail(APIView):

    def get_object(self, pk):
        try:
            return Activity.object.get(pk = pk)
        except Activity.DoesNotExist:
            raise Http404

    def get(self, request, pk, format = None):
        activity = self.get_object(pk)
        serilized_activities = ActivitiesSerializer(activity)
        return Response(serilized_activities.data)


