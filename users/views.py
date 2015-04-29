# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"
from allauth.account.views import _ajax_response,\
                                  PasswordChangeView,EmailView
import json
from django.conf import settings
from utils.form_utils import ajax_response
from rest_framework import viewsets, exceptions
from rest_framework.parsers import FileUploadParser,FormParser,MultiPartParser,JSONParser
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from django.contrib.auth.models import User
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.serializer import StudentsSerializer 
from students.models import Student
from .serializers import AuthTokenSerializer
from utils.forms import FileUploadForm
from rest_framework import status
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .serializers import UserProfilesSerializer, RequestSignupsSerializers
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout as auth_logout
from .models import RequestSignup,OrganizerConfirmation
from django.utils.translation import ugettext_lazy as _
from allauth.account.views import SignupView,ConfirmEmailView
from django.http import HttpResponse



def _set_ajax_response(_super):
    form_class = _super.get_form_class()
    form = _super.get_form(form_class)
    response = None
    if form.is_valid():
        response = _super.form_valid(form)
    else:
        response = _super.form_invalid(form)

    return response,form


def get_user_profile_data(user):
    profile = None
    data = None

    try:
        profile = Organizer.objects.get(user=user)
        data    = OrganizersSerializer(profile).data
    except Organizer.DoesNotExist:
        profile = Student.objects.get(user=user)
        data    = StudentsSerializer(profile).data

    return data




class RequestSignupViewSet(viewsets.ModelViewSet):
    queryset = RequestSignup.objects.all()
    serializer_class = RequestSignupsSerializers






class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfilesSerializer

    def retrieve(self, request):
        user = request.user

        if  user.is_anonymous():
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = get_user_profile_data(user)
        return Response(data)


    def logout(self,request):

        auth_logout(request)
        return Response(status=status.HTTP_200_OK)

    def verify_organizer_pre_signup_key(self,request,key):
        oc = get_object_or_404(OrganizerConfirmation,key=key)
        if oc.used:
            msg = _('Token de confirmacion ha sido usado')
            raise exceptions.ValidationError(msg)
        
        request_signup = oc.requested_signup
        request_signup_data = RequestSignupsSerializers(request_signup).data


        return Response(request_signup_data,status=status.HTTP_200_OK) 





class ObtainAuthTokenView(APIView):
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (FormParser, MultiPartParser, JSONParser,)
    renderer_classes = (JSONRenderer,)
    serializer_class = AuthTokenSerializer

    def post(self, request):

        serializer = self.serializer_class(data=request.data,context={'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        user_data = get_user_profile_data(user)


        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,'user':user_data})






class PhotoUploadView(APIView):
    parser_classes = (FileUploadParser,)


    def post(self, request):
        user = self.request.user
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile  = None
        data     = None
        photo    = None


        file_form = FileUploadForm(request.POST,request.FILES)
        if file_form.is_valid():
            photo = request.FILES['file']
        else:
            return Response(ajax_response(file_form),status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            profile = Organizer.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data    = OrganizersSerializer(profile).data
        except Organizer.DoesNotExist:
            profile = Student.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data    = StudentsSerializer(profile).data

        return Response(data)





class ChangeEmailView(APIView):

    def post(self, request, *args, **kwargs):
        res = None
        if "action_add" in request.POST:
            _super =  EmailView()
            _super.request = request._request
            response,form  = _set_ajax_response(_super)
            return _ajax_response(request, response, form=form)

        elif request.POST.get("email"):
            if "action_send" in request.POST:
                res = super(ChangeEmailView, self)._action_send(request)
            elif "action_remove" in request.POST:
                res = super(ChangeEmailView, self)._action_remove(request)
            elif "action_primary" in request.POST:
                res = super(ChangeEmailView, self)._action_primary(request)
            res = res or HttpResponseRedirect(reverse('account_email'))

        return _ajax_response(request, res)


class PasswordChange(APIView):


    def post(self,request, *args, **kwargs):
        _super_response = PasswordChangeView()
        _super_response.request = request._request
        _super_response.post(request, *args, **kwargs)

        response,form = _set_ajax_response(_super_response)
        return _ajax_response(request, response, form=form)


class ConfirmEmail(ConfirmEmailView):


    def post(self,request,*args,**kwargs):
        
        super(ConfirmEmail, self).post(request, *args, **kwargs)

        return HttpResponse(
            content_type="application/json",status=200)





# class SignUpCustomView(SignupView):


#     def post(self, request, *args, **kwargs):


#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():

#             email = form.cleaned_data.get('email',None)
#             user_type = form.cleaned_data.get('user_type','S')
#             if user_type == settings.ORGANIZER_TYPE:
#                 try:
#                     oc = OrganizerConfirmation.objects.\
#                         select_related('requested_signup').\
#                         get(requested_signup__email=email)
#                     oc.used = True
#                     oc.save()

#                 except OrganizerConfirmation.DoesNotExist:
#                     msg = unicode(_("Este correo no ha sido previamente validado"))
#                     response_data = {'form_errors':{'email':[msg]}}
                    
#                     return HttpResponse(json.dumps(response_data),
#                         content_type="application/json",status=400)

#             response = self.form_valid(form)
#         else:
#             response = self.form_invalid(form)


#         return _ajax_response(request,response,form=form)
