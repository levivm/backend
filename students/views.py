from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from activities.models import Activity
from activities.serializers import ActivitiesSerializer
from students.models import Student, WishList
from students.permissions import IsOwner
from students.serializer import StudentsSerializer
from utils.paginations import MediumResultsSetPagination, SmallResultsSetPagination
from utils.permissions import DjangoObjectPermissionsOrAnonReadOnly, IsStudent


class StudentViewSet(ModelViewSet):
    serializer_class = StudentsSerializer
    queryset = Student.objects.all()
    permission_classes = (DjangoObjectPermissionsOrAnonReadOnly, )


class StudentActivitiesViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentsSerializer
    pagination_class = SmallResultsSetPagination
    permission_classes = (IsAuthenticated, IsOwner)

    def get_serializer_context(self):
        context = super(StudentActivitiesViewSet,self).get_serializer_context()
        context.update({'show_reviews':True})
        return context

    def autocomplete(self, request, *args, **kwargs):
        student = self.get_object()
        activities = Activity.objects.by_student(student)
        serializer = ActivitiesAutocompleteSerializer(activities, many=True)
        result = serializer.data
        return Response(result)


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
