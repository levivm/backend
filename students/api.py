from models import Student
from serializers import StudentsSerializer

from django.htto import Http404

from rest_framework.views import APIView
from rest_framework.response import Response


class StudentDetail(APIView):
	def get_object(self, pk):
		try:
			return Student.object.get(pk = pk)
		except Student.DoesNotExist:
			raise Http404

	def get(self, request, pk, format = None):
		student = self.get_object(pk):
		serilized_students = StudentSerializer(student)
		return Response(serilized_students.data)


