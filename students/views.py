from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from activities.serializers import ActivitiesSerializer
from students.models import Student
from students.permissions import IsOwner
from students.serializer import StudentsSerializer
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly


class StudentViewSet(ModelViewSet):
    serializer_class = StudentsSerializer
    queryset = Student.objects.all()
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )


class StudentActivitiesViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentsSerializer
    permission_classes = (IsAuthenticated, IsOwner)

    def retrieve(self, request, *args, **kwargs):
        student = self.get_object()
        activities = [order.chronogram.activity for order in student.orders.all()]
        activities = list(set(activities))
        serializer = ActivitiesSerializer(activities, many=True)
        return Response(serializer.data)
