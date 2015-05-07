from rest_framework.viewsets import ModelViewSet
from students.models import Student
from students.serializer import StudentsSerializer
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly


class StudentViewSet(ModelViewSet):
    serializer_class = StudentsSerializer
    queryset = Student.objects.all()
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )