from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from activities.models import Activity
from activities.serializers import ActivitiesSerializer
from students.models import Student, WishList
from students.permissions import IsOwner
from students.serializer import StudentsSerializer
from utils.paginations import MediumResultsSetPagination
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly, IsStudent


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
        activities = [order.calendar.activity for order in student.orders.all()]
        activities = list(set(activities))
        serializer = ActivitiesSerializer(activities, many=True)
        return Response(serializer.data)


class WishListViewSet(ModelViewSet):
    serializer_class = ActivitiesSerializer
    queryset = WishList.objects.all()
    permission_classes = (IsAuthenticated, IsStudent)
    pagination_class = MediumResultsSetPagination

    def get_queryset(self):
        self.student = self.request.user.get_profile()
        return self.student.wish_list.all()

    def create(self, request, *args, **kwargs):
        try:
            activity = Activity.objects.get(id=request.data.get('activity_id'))
        except Activity.DoesNotExist:
            return Response('La actividad no existe', status=400)

        wish_list = self.get_queryset()
        if activity not in wish_list:
            self.add_to_wish_list(activity)
        else:
            self.remove_from_wish_list(activity)

        return Response('OK')

    def add_to_wish_list(self, activity):
        WishList.objects.create(student=self.student, activity=activity)

    def remove_from_wish_list(self, activity):
        wish_list_object = WishList.objects.get(student=self.student, activity=activity)
        wish_list_object.delete()
