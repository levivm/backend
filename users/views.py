# -*- coding: utf-8 -*-
# "Content-Type: text/plain; charset=UTF-8\n"
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework import viewsets, exceptions
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.models import Student
from students.serializer import StudentsSerializer
from utils.form_utils import ajax_response
from utils.forms import FileUploadForm
from .models import RequestSignup, OrganizerConfirmation
from .serializers import RequestSignUpSerializer, UsersSerializer


def _set_ajax_response(_super):
    form_class = _super.get_form_class()
    form = _super.get_form(form_class)
    if form.is_valid():
        response = _super.form_valid(form)
    else:
        response = _super.form_invalid(form)

    return response, form


def get_user_profile_data(user):
    try:
        profile = Organizer.objects.get(user=user)
        data = OrganizersSerializer(profile).data
    except Organizer.DoesNotExist:
        profile = Student.objects.get(user=user)
        data = StudentsSerializer(profile).data

    return data


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password1', 'password2'))


class RequestSignupViewSet(viewsets.ModelViewSet):
    queryset = RequestSignup.objects.all()
    serializer_class = RequestSignUpSerializer


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        if user.is_anonymous():
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = get_user_profile_data(user)

        return Response(data)

    def logout(self, request):

        auth_logout(request)
        return Response(status=status.HTTP_200_OK)

    def verify_organizer_pre_signup_key(self, request, key):
        oc = get_object_or_404(OrganizerConfirmation, key=key)

        if oc.used:
            msg = _('Token de confirmacion ha sido usado')
            raise exceptions.ValidationError(msg)

        request_signup = oc.requested_signup
        request_signup_data = RequestSignUpSerializer(request_signup).data

        return Response(request_signup_data, status=status.HTTP_200_OK)


class PhotoUploadView(APIView):
    parser_classes = (FileUploadParser,)

    def post(self, request):
        user = self.request.user
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile = None
        data = None
        photo = None

        file_form = FileUploadForm(request.POST, request.FILES)
        if file_form.is_valid():
            photo = request.FILES['file']
        else:
            return Response(ajax_response(file_form), status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            profile = Organizer.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data = OrganizersSerializer(profile).data
        except Organizer.DoesNotExist:
            profile = Student.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data = StudentsSerializer(profile).data

        return Response(data)

# class ChangeEmailView(APIView):
#     def post(self, request, *args, **kwargs):
#         res = None
#         if "action_add" in request.POST:
#             _super = EmailView()
#             _super.request = request._request
#             response, form = _set_ajax_response(_super)
#             return _ajax_response(request, response, form=form)
#
#         elif request.POST.get("email"):
#             if "action_send" in request.POST:
#                 res = super(ChangeEmailView, self)._action_send(request)
#             elif "action_remove" in request.POST:
#                 res = super(ChangeEmailView, self)._action_remove(request)
#             elif "action_primary" in request.POST:
#                 res = super(ChangeEmailView, self)._action_primary(request)
#             res = res or HttpResponseRedirect(reverse('account_email'))
#
#         return _ajax_response(request, res)
#
#
# class PasswordChange(APIView):
#     def post(self, request, *args, **kwargs):
#         _super_response = PasswordChangeView()
#         _super_response.request = request._request
#         response, form = _set_ajax_response(_super_response)
#         return _ajax_response(request, response, form=form)
#
#
# class ConfirmEmail(ConfirmEmailView):
#     def post(self, request, *args, **kwargs):
#         super(ConfirmEmail, self).post(request, *args, **kwargs)
#
#         return HttpResponse(
#             content_type="application/json", status=status.HTTP_200_OK)
