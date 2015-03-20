from django.shortcuts import render
from allauth.account.views import SignupView,PasswordResetView,_ajax_response,PasswordChangeView,LoginView,EmailView
# Create your views here.
import json
from utils.form_utils import ajax_response
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.serializer import StudentsSerializer 
from students.models import Student
from utils.forms import FileUploadForm
from utils.form_utils import ajax_response
from rest_framework import status
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from .serializers import UserProfilesSerializer




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
    print 'formm,',form
    response = None
    if form.is_valid():
        response = _super.form_valid(form)
    else:
        response = _super.form_invalid(form)

    return response,form




class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserProfilesSerializer

    def retrieve(self, request):
        user = self.request.user
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




        # ...
        # do some staff with uploaded file
        # ...

        return Response(data)


class PhotoUploadView(APIView):
    parser_classes = (FileUploadParser,)


    def post(self, request):
        user = self.request.user
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile  = None
        data     = None
        photo    = None


        print "HOLAAAAAAAAAAAAAAAAAa"

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



class ChangeEmailView(EmailView):



    def post(self, request, *args, **kwargs):
        res = None
        if "action_add" in request.POST:
            _super =  super(ChangeEmailView, self)
            response,form = _set_ajax_response(_super)
            res = super(ChangeEmailView, self).post(request, *args, **kwargs)
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

    #     print _super_response
    #     #print "es un post"
    #     response,form = set_ajax_response(_response)
    #     #print response,form
    #     return _ajax_response(request, response, form=form)

class PasswordChange(PasswordChangeView):



    def post(self, request, *args, **kwargs):

        _super_response =  super(PasswordChange, self)
        _super_response.post(request, *args, **kwargs)
        
        
        
        response,form = _set_ajax_response(_super_response)
        return _ajax_response(request, response, form=form)



class ResetPassword(PasswordResetView):



    def post(self, request, *args, **kwargs):

        _super_response =  super(ResetPassword, self)
        
        
        
        response,form = _set_ajax_response(_super_response)
        return _ajax_response(request, response, form=form)

        # #super(ResetPassword, self).post(request, *args, **kwargs)
        # print s.__attr__
        # #print _s
        # #print super(super(ResetPassword, self).__class__,self)
        # #print super(ResetPassword, self).get_context_data(**kwargs)
        # form_class =  super(ResetPassword, self).get_form_class()
        # form = super(ResetPassword, self).get_form(form_class)
        # print form.errors
        #print "eror",_ajax_response(self.request, response, form=form)
        #print "eror",ajax_response(form._errors)
        #print "eror",form.is_valid()


    # def get_context_data(self, **kwargs):
    #     ret = super(ResetPassword, self).get_context_data(**kwargs)
    #     print "re",ret
    #     # NOTE: For backwards compatibility
    #     ret['password_reset_form'] = super(ResetPassword, self).get_form_class()
    #     # (end NOTE)
    #     return ret

# class SignUpAjax(SignupView):


#     # def post(self, request, *args, **kwargs):


#     #     print super(SignUpAjax, self)(self)
#     #     #ret = super(SignUpAjax, self).get_context_data(**kwargs)
#     #     #print "MIRAME ret",ret
#     #     return HttpResponse(json.dumps({'hola':'asdasd'}), content_type="application/json")
#     #     return ajax_response(ret['form'])
#         # form = self.form_class(request.POST)
#         # if form.is_valid():
#         #     # <process form cleaned data>
#         #     return HttpResponseRedirect('/success/')

#         # return render(request, self.template_name, {'form': form})


#     def post(self, request, *args, **kwargs):

#         print "soy ajaxxxxxxxxxxx",request.is_ajax()
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
#     #     #print "POSTTTTTTT",post
#     #     print post.request
#     #     return post
#         #form = super(SignUpAjax, self).get_form(form_class)
#         #if form.is_valid():
#         #    response = super(SignUpAjax, self).form_valid(form)
#         #else:
#         #    response = super(SignUpAjax, self).form_invalid(form)
#         #return _ajax_response(self.request, response, form=form)
#         #ret = .get_context_data(**kwargs)
#         #ret['all_tags'] = "ss"
#         #print ret['form'].errors
#         #print ret
#         #print ajax_response(ret['form'])
#         #json.dumps(ret)
#         #return HttpResponse(, content_type="application/json")
#         #return json.dumps(response_data)
#         #return _ajax_response(self.request, response, form=form)
#         #return ret
