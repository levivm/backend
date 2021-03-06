from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from requests.exceptions import HTTPError
from rest_framework.exceptions import ValidationError
from rest_framework.generics import GenericAPIView, get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from social.apps.django_app.utils import psa

from activities.mixins import MongoMixin
from authentication.mixins import SignUpMixin, ValidateTokenMixin, InvalidateTokenMixin
from authentication.models import ResetPasswordToken, ConfirmEmailToken
from authentication.permissions import IsNotAuthenticated
from authentication.serializers import AuthTokenSerializer, SignUpStudentSerializer, \
    ChangePasswordSerializer, ForgotPasswordSerializer, ChangeEmailSerializer
from authentication.tasks import ChangePasswordNoticeTask, SendEmailResetPasswordTask, \
    SendEmailConfirmEmailTask, SendEmailHasChangedTask, SendEmailSignUpRequestNotificationTask, \
    SendEmailSignUpCouponTask
from balances.models import Balance
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from referrals.mixins import ReferralMixin
from students.models import Student
from students.serializer import StudentsSerializer
from users.models import RequestSignup, OrganizerConfirmation
from users.views import get_user_profile_data
from users.serializers import RequestSignUpSerializer


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
        data = {'token': user.auth_token.key, 'user': profile_data}

        return Response(data)


class SignUpStudentView(MongoMixin, SignUpMixin, GenericAPIView): #, ReferralMixin):
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
        self.confirm_email_handler(user)
        token = self.create_token(user)

        #self.referral_handler(referred_id=profile.id)
        self.send_coupon(student=profile)

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

    def confirm_email_handler(self, user):
        confirm_email_token = ConfirmEmailToken.objects.create(user=user, email=user.email)
        task = SendEmailConfirmEmailTask()
        task.delay(confirm_email_token.id)

    def send_coupon(self, student):
        leads = self.get_collection(name='leads')
        if leads.find({'email': student.user.email}).count() == 0:
            task = SendEmailSignUpCouponTask()
            task.delay(student_id=student.id)

class VerifySignupOrganizerToken(APIView):

    def get(self, request, key):
        oc = get_object_or_404(OrganizerConfirmation, key=key)

        if oc.used:
            msg = _('Token de confirmacion ha sido usado')
            raise ValidationError(msg)

        request_signup = oc.requested_signup
        request_signup_data = RequestSignUpSerializer(request_signup).data

        return Response(request_signup_data, status=status.HTTP_200_OK)

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
        self.create_balance(profile=profile)

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
            raise ValidationError({'password': ['La contraseña es requerida.']})

        return password

    def verify_organizer_pre_signup_key(self, request, key):
        oc = get_object_or_404(OrganizerConfirmation, key=key)

        if oc.used:
            msg = _('Token de confirmacion ha sido usado')
            raise ValidationError(msg)

        request_signup = oc.requested_signup
        request_signup_data = RequestSignUpSerializer(request_signup).data

        return Response(request_signup_data, status=status.HTTP_200_OK)

    def create_balance(self, profile):
        Balance.objects.create(organizer=profile)


class SocialAuthView(ReferralMixin, GenericAPIView):
    """
    Class to login or register an student using Facebook
    """

    def post(self, request, *args, **kwargs):
        provider = kwargs.get('provider')

        token = self.request.data.get('access_token')
        if token is None:
            return Response({'error': 'The access_token parameter is required'}, status=400)

        try:
            user = self.register_by_access_token(request, provider, token)
        except HTTPError:
            return Response({'error': 'No se puede conectar a %s' % provider}, status=400)

        profile_data = self.get_profile_data(user.student_profile)

        self.referral_handler(referred_id=user.student_profile.id)
        return Response({'user': profile_data, 'token': user.auth_token.key})

    @method_decorator(psa())
    def register_by_access_token(self, request, backend, token):
        return request.backend.do_auth(token)

    def get_profile_data(self, profile):
        return StudentsSerializer(profile).data


class ChangePasswordView(GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.set_password(serializer.validated_data['password1'])
        request.user.save(update_fields=['password'])

        task = ChangePasswordNoticeTask()
        task.delay(request.user.id)

        return Response('OK')

    def get_serializer_context(self):
        context = super(ChangePasswordView, self).get_serializer_context()
        context['user'] = self.request.user
        return context


class ForgotPasswordView(InvalidateTokenMixin, GenericAPIView):
    permission_classes = (IsNotAuthenticated,)
    serializer_class = ForgotPasswordSerializer
    model = ResetPasswordToken

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        user = self.get_user()

        self.invalidate_token(user)
        reset_password = ResetPasswordToken.objects.create(user=user)
        task = SendEmailResetPasswordTask()
        task.delay(reset_password.id)
        return Response('OK')

    def get_user(self):
        user = User.objects.get(email=self.request.data.get('email'))
        return user


class ResetPasswordView(ValidateTokenMixin, GenericAPIView):
    model = ResetPasswordToken

    def post(self, request, *args, **kwargs):
        request_password = self.validate_token(request.data.get('token'))
        password = self.validate_password()

        request_password.user.set_password(password)
        request_password.user.save(update_fields=['password'])

        task = ChangePasswordNoticeTask()
        task.delay(request_password.user.id)

        request_password.used = True
        request_password.save(update_fields=['used'])

        return Response('OK')

    def validate_password(self):
        password1 = self.request.data.get('password1')
        password2 = self.request.data.get('password2')

        if password1 and password2 and password1 == password2:
            return password1

        raise ValidationError(_('Las contraseñas no son iguales.'))


class ConfirmEmailView(ValidateTokenMixin, GenericAPIView):
    model = ConfirmEmailToken

    def post(self, request, *args, **kwargs):
        confirm_email = self.validate_token(request.data.get('token'))

        confirm_email.user.email = confirm_email.email
        confirm_email.user.save(update_fields=['email'])

        profile = confirm_email.user.get_profile()
        profile.verified_email = True
        profile.save(update_fields=['verified_email'])

        confirm_email.used = True
        confirm_email.save(update_fields=['used'])

        if request.data.get('change_email'):
            task = SendEmailHasChangedTask()
            task.delay(confirm_email_id=confirm_email.id)

        profile_data = self.get_profile_data(profile)

        return Response(profile_data)

    def get_profile_data(self, profile):
        if isinstance(profile, Organizer):
            serializer_class = OrganizersSerializer
        else:
            serializer_class = StudentsSerializer

        return serializer_class(profile).data


class ChangeEmailView(InvalidateTokenMixin, GenericAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangeEmailSerializer
    model = ConfirmEmailToken

    def post(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        email = self.get_email()
        self.invalidate_token(request.user)

        confirm_email = ConfirmEmailToken.objects.create(
            user=request.user,
            email=email)

        task = SendEmailConfirmEmailTask()
        task.delay(confirm_email.id, url_params='change_email=true')

        profile = confirm_email.user.get_profile()
        profile.verified_email = False
        profile.save(update_fields=['verified_email'])

        return Response('OK')

    def get_email(self):
        email = self.request.data.get('email')
        return email


class VerifyConfirmEmailTokenView(ValidateTokenMixin, GenericAPIView):
    model = ConfirmEmailToken

    def get(self, request, token, *args, **kwargs):
        self.validate_token(token=token)
        return Response({'OK'})


class VerifyResetPasswordTokenView(ValidateTokenMixin, GenericAPIView):
    model = ResetPasswordToken

    def get(self, request, token, *args, **kwargs):
        self.validate_token(token=token)
        return Response({'OK'})


class RequestSignupViewSet(viewsets.ModelViewSet):
    queryset = RequestSignup.objects.all()
    serializer_class = RequestSignUpSerializer

    def perform_create(self, serializer):
        request_signup = serializer.save()
        task = SendEmailSignUpRequestNotificationTask()
        task.delay(request_signup.id)
