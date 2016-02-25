from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from activities.serializers import ActivitiesSerializer
from activities.models import Activity
from .models import Student
from .permissions import IsOwner
from .serializer import StudentsSerializer
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly
from utils.paginations import SmallResultsSetPagination



class StudentViewSet(ModelViewSet):
    serializer_class = StudentsSerializer
    queryset = Student.objects.all()
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )


class StudentActivitiesViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentsSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = (IsAuthenticated, IsOwner)

    def retrieve(self, request, *args, **kwargs):
        student = self.get_object()
        status = request.query_params.get('status')
        activities = Activity.objects.by_student(student, status)
        page = self.paginate_queryset(activities)
        if page is not None:
            serializer = ActivitiesSerializer(page, many=True,
                                              context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)

        serializer = ActivitiesSerializer(activities, many=True, 
                                          context=self.get_serializer_context())
        result = serializer.data
        return Response(result)
