from django.shortcuts import render
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
#from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


from .models import Organizer
from .serializers import OrganizersSerializer,InstructorsSerializer
from activities.serializers import ActivitiesSerializer



# Create your views here.

def signup(request):
    return render(request,'organizers/signup.html',{})




class OrganizerViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions
    """
    queryset = Organizer.objects.all()
    serializer_class = OrganizersSerializer
    #authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)


    def activities(self,request,pk=None):
        organizer = self.get_object()
        activities = organizer.activity_set.all()
        data = ActivitiesSerializer(activities,many=True).data
        return Response(data)



    # def partial_update(self, request, pk=None):
    #     print "REEE",request.POST

    #     return Response(status=200)
        


class InstructorViewSet(viewsets.ModelViewSet):
    serializer_class = InstructorsSerializer
    lookup_url_kwarg = 'instructor_id'


    def get_queryset(self):
        organizer_id = self.kwargs.get('organizer_id',None)
        organizer = get_object_or_404(Organizer,pk=organizer_id)
        print "instructors",organizer.instructors.all()
        return organizer.instructors.all()