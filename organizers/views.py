from django.shortcuts import render
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView


# Create your views here.

def signup(request):
	return render(request,'organizers/signup.html',{})


class PhotoUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def put(self, request, filename, format=None):
        file_obj = request.data['file']
        user_id  = request.data['user_id']
        
        # ...
        # do some staff with uploaded file
        # ...
        return Response(status=204)