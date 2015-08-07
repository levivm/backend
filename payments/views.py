from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
import json


# Create your views here.




class PayUNotificationPayment(APIView):

	def post(self, request, *args, **kwargs):
		# print("request",request.POST)
		print(json.dumps(request.POST))
		return Response({'data': request.POST})