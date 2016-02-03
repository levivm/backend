from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.response import Response

from authentication.mixins import SignUpMixin
from authentication.serializers import AuthTokenSerializer, SignUpStudentSerializer
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.models import Student
from students.serializer import StudentsSerializer
from users.models import RequestSignup
from users.views import get_user_profile_data


class LoginView(GenericAPIView):
    """
    Class to login users
    """
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})

        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        profile_data = get_user_profile_data(user=user)
        token = Token.objects.get(user=user)
        data = {'token': token.key, 'user': profile_data}

        return Response(data)


class SignUpStudentView(SignUpMixin, GenericAPIView):
    """
    Class to register students
    """
    serializer_class = SignUpStudentSerializer
    permissions = ['students.change_student']
    profile_serializer = StudentsSerializer
    group_name = 'Students'

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = self.create_user(serializer)
        profile = self.create_profile(user=user)
        profile_data = self.get_profile_data(profile)
        self.assign_group(user)
        self.assign_permissions(user, profile)
        token = self.create_token(user)

        return Response({'user': profile_data, 'token': token.key})

    def create_user(self, serializer):
        return User.objects.create_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password1'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
        )

    def create_profile(self, user):
        return Student.objects.create(user=user)


class SignUpOrganizerView(SignUpMixin, GenericAPIView):
    """
    Class to register organizers
    """
    permissions = ['organizers.change_organizer']
    profile_serializer = OrganizersSerializer
    group_name = 'Organizers'

    def post(self, request, *args, **kwargs):
        self.request_signup = self.get_object()
        self.password = self.validate_password()

        user = self.create_user()
        profile = self.create_profile(user=user)
        profile_data = self.get_profile_data(profile)
        self.assign_group(user=user)
        self.assign_permissions(user, profile)
        token = self.create_token(user)

        return Response({'user': profile_data, 'token': token.key})

    def get_object(self):
        return get_object_or_404(RequestSignup,
                                 approved=True,
                                 organizerconfirmation__key=self.kwargs.get('token'),
                                 organizerconfirmation__used=False)

    def create_user(self):
        return User.objects.create_user(
            username=self.request_signup.name.replace(' ', '.'),
            email=self.request_signup.email,
            password=self.password,
        )

    def create_profile(self, user):
        return Organizer.objects.create(
            user=user,
            name=self.request_signup.name,
            telephone=self.request_signup.telephone,
        )

    def validate_password(self):
        password = self.request.data.get('password')
        if not password:
            raise ValidationError({'password': ['The password is required.']})

        return password
