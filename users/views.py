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
from .serializers import RequestSignupsSerializers, UsersSerializer


def _set_ajax_response(_super):
    form_class = _super.get_form_class()
    form = _super.get_form(form_class)
    response = None
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
    serializer_class = RequestSignupsSerializers


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def retrieve(self, request):
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
        request_signup_data = RequestSignupsSerializers(request_signup).data

        return Response(request_signup_data, status=status.HTTP_200_OK)


# class ObtainAuthTokenView(ReferralMixin):
#     throttle_classes = ()
#     permission_classes = ()
#     parser_classes = (FormParser, MultiPartParser, JSONParser,)
#     renderer_classes = (JSONRenderer,)
#     serializer_class = AuthTokenSerializer
#
#     @sensitive_post_parameters_m
#     def dispatch(self, request, *args, **kwargs):
#         self.is_sign_up = request.POST.get('user_type')
#         self.request_copy = request
#         return super(ObtainAuthTokenView, self).dispatch(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#         response = self.register_or_login(*args, **kwargs)
#
#         if response:
#             return response
#
#         auth_data = self.get_auth_data()
#
#         serializer = self.serializer_class(data=auth_data, context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#
#         user_data = get_user_profile_data(user)
#
#         token, created = Token.objects.get_or_create(user=user)
#         data = {'token': token.key, 'user': user_data}
#         return super(ObtainAuthTokenView, self).post(data, request, *args, **kwargs)
#
#     def get_auth_data(self):
#         if self.is_sign_up:
#             auth_data = {
#                 'email': self.request.data.get('email'),
#                 'password': self.request.data.get('password1'),
#             }
#         else:
#             auth_data = {
#                 'email': self.request.data.get('login'),
#                 'password': self.request.data.get('password')
#             }
#
#         return auth_data
#
#     def register_or_login(self, *args, **kwargs):
#         if self.is_sign_up:
#             signup_response = SignupView().dispatch(self.request_copy, *args, **kwargs)
#             if (signup_response.status_code == status.HTTP_400_BAD_REQUEST):
#                 return signup_response
#
#         else:
#             login_response = LoginView().dispatch(self.request_copy, *args, **kwargs)
#             if (login_response.status_code == status.HTTP_400_BAD_REQUEST):
#                 return login_response


# class RestFacebookLogin(ReferralMixin):
#     """
#     Login or register a user based on an authentication token coming
#     from Facebook.
#     Returns user data including session id.
#     """
#
#     permission_classes = (AllowAny,)
#
#     def dispatch(self, *args, **kwargs):
#         return super(RestFacebookLogin, self).dispatch(*args, **kwargs)
#
#     def post(self, request, *args, **kwargs):
#
#         try:
#             original_request = request._request
#             auth_token = request.data.get('auth_token', '')
#             # Find the token matching the passed Auth token
#             app = SocialApp.objects.get(provider='facebook')
#             fb_auth_token = SocialToken(app=app, token=auth_token)
#
#             # check token against facebook
#             login = fb_complete_login(original_request, app, fb_auth_token)
#             login.token = fb_auth_token
#             login.state = SocialLogin.state_from_request(original_request)
#
#             # add or update the user into users table
#             complete_social_login(original_request, login)
#             # Create or fetch the session id for this user
#             user = original_request.user
#
#             token, _ = Token.objects.get_or_create(user=user)
#
#             # token, _ = Token.objects.get_or_create(user=original_request.user)
#             # if we get here we've succeeded
#             user_data = get_user_profile_data(user)
#
#             data = {
#                 'user': user_data,
#                 'token': token.key,
#             }
#
#             # return Response(
#             #     status=status.HTTP_200_OK,
#             #     data=data
#             # )
#             return super(RestFacebookLogin, self).post(data, request, *args, **kwargs)
#
#         except Exception as error:
#             return Response(status=status.HTTP_401_UNAUTHORIZED, data={
#                 'detail': error,
#             })


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
