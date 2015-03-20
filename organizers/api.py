from .models import Organizer
from .models import Instructor

from .serializers import OrganizersSerializer
from .serializers import InstructorsSerializer

from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response


class OrganizerDetail(APIView):
	def get_object(self, pk):
		try:
			return Organizer.object.get(pk = pk)
		except Organizer.DoesNotExist:
			raise Http404

	def get(self, request, pk, format = None):
		organizer = self.get_object(pk)
		serilized_organizers = OrganizersSerializer(organizer)
		return Response(serilized_organizers.data)


class InstructorDetail(APIView):
	def get_object(self, pk):
		try:
			return Instructor.object.get(pk = pk)
		except Instructor.DoesNotExist:
			raise Http404

	def get(self, request, pk, format = None):
		instructor = self.get_object(pk)
		serilized_instructors = (instructor)
		return Response(serilized_instructors.data)

