# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"


# from django.shortcuts import render
from allauth.account.views import _ajax_response,\
                                  PasswordChangeView,EmailView
# Create your views here.
# from allauth.account.models import EmailConfirmation
# import json
from utils.form_utils import ajax_response
#from django.http import HttpResponse
from rest_framework import viewsets, exceptions
from rest_framework.parsers import FileUploadParser,FormParser,MultiPartParser,JSONParser
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
#from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.serializer import StudentsSerializer 
from students.models import Student
from .serializers import AuthTokenSerializer
from utils.forms import FileUploadForm
#from utils.form_utils import ajax_response
from rest_framework import status
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .serializers import UserProfilesSerializer, RequestSignupsSerializers
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from django.contrib.auth import logout as auth_logout
from .models import RequestSignup,OrganizerConfirmation
from django.utils.translation import ugettext_lazy as _



# def _ajax_response(request, response, form=None):
#     if request.is_ajax():
#         if (isinstance(response, HttpResponseRedirect)
#                 or isinstance(response, HttpResponsePermanentRedirect)):
#             redirect_to = response['Location']
#         else:
#             redirect_to = None
#         response = get_adapter().ajax_response(request,
#                                                response,
#                                                form=form,
#                                                redirect_to=redirect_to)
#     return HttpResponse({'hola':1}, content_type="application/json")
#     return response




# def ajax_response_(request, response, redirect_to=None, form=None):
#     data = {}
#     if redirect_to:
#         status = 200
#         data['location'] = redirect_to
#     if form:
#         if form.is_valid():
#             status = 200
#         else:
#             status = 400
#             data['form_errors'] = form._errors
#         if hasattr(response, 'render'):
#             response.render()
#         data['html'] = response.content.decode('utf8')
#     return HttpResponse(json.dumps(data),
#                         status=status,
#                         content_type='application/json')


 #ret = super(PasswordResetView, self).get_context_data(**kwargs)





def _set_ajax_response(_super):
    form_class = _super.get_form_class()
    form = _super.get_form(form_class)
    response = None
    if form.is_valid():
        response = _super.form_valid(form)
    else:
        response = _super.form_invalid(form)

    return response,form



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
        profile  = None
        data     = None

        try:
            profile = Organizer.objects.get(user=user)
            data    = OrganizersSerializer(profile).data
        except Organizer.DoesNotExist:
            profile = Student.objects.get(user=user)
            data    = StudentsSerializer(profile).data

        return Response(data)


    def logout(self,request):

        auth_logout(request)
        return Response(status=status.HTTP_200_OK)

    def verify_organizer_pre_signup_key(self,request,key):
        oc = get_object_or_404(OrganizerConfirmation,key=key)
        if oc.used:
            msg = _('Token de confirmación ha sido usado')
            raise exceptions.ValidationError(msg)
        
        return Response(status=status.HTTP_200_OK) 





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
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key})






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

    # def post(self, request, *args, **kwargs):

       
    #     _response = super(ChangeEmailView, self).post(request, *args, **kwargs)
    #     _super_response = super(ChangeEmailView, self)

    #     response,form = set_ajax_response(_response)
    #     return _ajax_response(request, response, form=form)

class PasswordChange(APIView):

    # authentication_classes = (TokenAuthentication,)

    def post(self,request, *args, **kwargs):
        _super_response = PasswordChangeView()
        _super_response.request = request._request
        _super_response.post(request, *args, **kwargs)

        response,form = _set_ajax_response(_super_response)
        return _ajax_response(request, response, form=form)



# class ResetPassword(PasswordResetView):



#     def post(self, request, *args, **kwargs):

#         _super_response =  super(ResetPassword, self)
        
        
        
#         response,form = _set_ajax_response(_super_response)
#         return _ajax_response(request, response, form=form)

        # #super(ResetPassword, self).post(request, *args, **kwargs)
        # form_class =  super(ResetPassword, self).get_form_class()
        # form = super(ResetPassword, self).get_form(form_class)


    # def get_context_data(self, **kwargs):
    #     ret = super(ResetPassword, self).get_context_data(**kwargs)
    #     # NOTE: For backwards compatibility
    #     ret['password_reset_form'] = super(ResetPassword, self).get_form_class()
    #     # (end NOTE)
    #     return ret

# class SignUpAjax(SignupView):


#     # def post(self, request, *args, **kwargs):


#     #     #ret = super(SignUpAjax, self).get_context_data(**kwargs)
#     #     return HttpResponse(json.dumps({'hola':'asdasd'}), content_type="application/json")
#     #     return ajax_response(ret['form'])
#         # form = self.form_class(request.POST)
#         # if form.is_valid():
#         #     # <process form cleaned data>
#         #     return HttpResponseRedirect('/success/')

#         # return render(request, self.template_name, {'form': form})


#     def post(self, request, *args, **kwargs):

#         form_class = self.get_form_class()
#         form = self.get_form(form_class)
#         if form.is_valid():
#             response = self.form_valid(form)
#         else:
#             response = self.form_invalid(form)

#         return ajax_response_(request,response,form=form)

#         return HttpResponse(json.dumps({'data':1}),
#                     status=200,
#                     content_type='application/json')

#     # def post(self, request, *args, **kwargs):


#     #     post = super(SignUpAjax, self).post(request, *args, **kwargs)
#     #     return post
#         #form = super(SignUpAjax, self).get_form(form_class)
#         #if form.is_valid():
#         #    response = super(SignUpAjax, self).form_valid(form)
#         #else:
#         #    response = super(SignUpAjax, self).form_invalid(form)
#         #return _ajax_response(self.request, response, form=form)
#         #ret = .get_context_data(**kwargs)
#         #ret['all_tags'] = "ss"
#         #json.dumps(ret)
#         #return HttpResponse(, content_type="application/json")
#         #return json.dumps(response_data)
#         #return _ajax_response(self.request, response, form=form)
#         #return ret
