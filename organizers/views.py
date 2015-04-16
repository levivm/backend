from django.shortcuts import render
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
#from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from .models import Organizer
from .serializers import OrganizersSerializer
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
        




