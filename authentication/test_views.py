import json
import urllib

import mock
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from model_mommy import mommy
from requests.exceptions import HTTPError
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase
from social.apps.django_app.default.models import UserSocialAuth

from authentication.models import ResetPasswordToken, ConfirmEmailToken
from balances.models import Balance
from locations.models import City
from organizers.factories import OrganizerFactory
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.factories import StudentFactory
from students.models import Student
from students.serializer import StudentsSerializer
from users.factories import RequestSignUpFactory, UserFactory
from users.models import RequestSignup
from utils.models import EmailTaskRecord
from utils.tests import BaseAPITestCase


class LoginViewTest(APITestCase):
    """
    Tests for LoginView
    """

    def setUp(self):
        # Users
        self.password = '12345678'
        self.student = StudentFactory(user__password=self.password)
        self.organizer = OrganizerFactory(user__password=self.password)

        # Tokens
        self.student_token = Token.objects.create(user=self.student.user)
        self.organizer_token = Token.objects.create(user=self.organizer.user)

        # URL
        self.url = reverse('auth:login')

    def test_login_student_success(self):
        """
        Test login success for a student
        """

        data = {
            'email': self.student.user.email,
            'password': self.password,
        }

        content = {
            'user': StudentsSerializer(self.student).data,
            'token': self.student_token.key,
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, content)

    def test_login_organizer_success(self):
        """
        Test login success for an organizer
        """

        data = {
            'email': self.organizer.user.email,
            'password': self.password,
        }

        content = {
            'user': OrganizersSerializer(self.organizer).data,
            'token': self.organizer_token.key,
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, content)


class SignUpStudentViewTest(APITestCase):
    """
    Test for SignUpStudentView
    """

    def setUp(self):
        self.url = reverse('auth:signup_student')
        self.student_group = Group.objects.create(name='Students')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_student_signup_success(self, send_mail):
        """
        Test case success for a student sign up
        """
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'jack.bauer@example.com',
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'email': 'jack.bauer@example.com',
            'first_name': 'Jack',
            'last_name': 'Bauer',
            'password1': 'jackisthebest',
        }

        response = self.client.post(self.url, urllib.parse.urlencode(data),
                                    content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(User.objects.filter(
            email='jack.bauer@example.com',
            username='jack.bauer').exists())

        student = Student.objects.last()
        content = {
            'user': StudentsSerializer(student).data,
            'token': student.user.auth_token.key,
        }

        self.assertEqual(response.data, content)
        self.assertIn(self.student_group, student.user.groups.all())
        self.assertTrue(student.user.has_perm('students.change_student', student))
        self.assertTrue(ConfirmEmailToken.objects.filter(user=student.user, used=False).exists())
        self.assertTrue(EmailTaskRecord.objects.filter(
            to='jack.bauer@example.com',
            status='sent').exists())


class SignUpOrganizerViewTest(APITestCase):
    """
    Test for SignUpOrganizerView
    """

    def setUp(self):
        with mock.patch('users.tasks.SendEmailOrganizerConfirmationTask.delay'):
            self.request_signup = RequestSignUpFactory(
                email='jack.bauer@example.com',
                name='Counter Terrorism Unit')
            self.request_signup.approved = True
            self.request_signup.save()

        self.organizer_group = Group.objects.create(name='Organizers')
        self.url = reverse('auth:signup_organizer',
                           kwargs={'token': self.request_signup.organizerconfirmation.key})

    def test_signup_success(self):
        """
        Test the case for signup success
        """
        data = {'password': 'jackisthebest'}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        organizer = Organizer.objects.last()
        content = {
            'user': OrganizersSerializer(organizer).data,
            'token': organizer.user.auth_token.key,
        }

        self.assertEqual(response.data, content)
        self.assertTrue(Balance.objects.filter(
            organizer=organizer,
            available=0,
            unavailable=0).exists())

    def test_validate_password(self):
        """
        Test the password is required
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'password': ['La contraseña es requerida.']})

    def test_validate_request_signup_approved(self):
        """
        404 if the request signup is not approved
        """

        self.request_signup.approved = False
        self.request_signup.save()
        data = {'password': 'jackisthebest'}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_token_exists(self):
        """
        404 if the token doesn't exists
        """

        url = reverse('auth:signup_organizer', args=('12345',))
        data = {'password': 'jackisthebest'}

        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_token_not_used(self):
        """
        404 if the token has been used
        """

        self.request_signup.organizerconfirmation.used = True
        self.request_signup.organizerconfirmation.save()

        data = {'password': 'jackisthebest'}

        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SocialAuthViewTest(APITestCase):
    """
    Tests for SocialAuthView
    """

    def setUp(self):
        self.url = reverse('auth:social_login_signup', kwargs={'provider': 'facebook'})

    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_login_success(self, get_json):
        """
        Test social login for student
        """

        student = StudentFactory(user__first_name='Geralt', user__last_name='De Rivia',
                                 user__email='derivia@witcher.com')
        token = Token.objects.create(user=student.user)
        UserSocialAuth.objects.create(user=student.user, uid='123456789', provider='facebook')
        user_counter = User.objects.count()

        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'link': 'https://www.facebook.com/app_scoped_user_id/123456789',
            'locale': 'en_US',
            'name': 'Geralt De Rivia',
            'timezone': -5,
            'verified': True,
        }

        response = self.client.post(self.url, data={
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})

        content = {
            'user': StudentsSerializer(student).data,
            'token': token.key,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), user_counter)
        self.assertEqual(response.data, content)

    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_login_fail(self, get_json):
        get_json.side_effect = HTTPError('Bad request for url')

        response = self.client.post(self.url, data={
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_signup_success(self, get_json, send_mail):
        user_counter = User.objects.count()
        student_group = Group.objects.create(name='Students')

        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'link': 'https://www.facebook.com/app_scoped_user_id/123456789',
            'locale': 'en_US',
            'name': 'Geralt De Rivia',
            'timezone': -5,
            'verified': True,
        }

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'derivia@witcher.com',
            'status': 'sent',
            'reject_reason': None
        }]

        response = self.client.post(self.url, data={
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})

        student = Student.objects.last()
        content = {
            'user': StudentsSerializer(student).data,
            'token': student.user.auth_token.key,
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), user_counter + 1)
        self.assertEqual(response.data, content)
        self.assertEqual(student.user.username, 'geralt.derivia')
        self.assertEqual(student.user.email, 'derivia@witcher.com')
        self.assertEqual(student.gender, Student.MALE)
        self.assertIn(student_group, student.user.groups.all())
        self.assertTrue(student.user.has_perm('students.change_student', student))
        self.assertTrue(ConfirmEmailToken.objects.filter(user=student.user, used=False).exists())
        self.assertTrue(EmailTaskRecord.objects.filter(
            to='derivia@witcher.com',
            status='sent').exists())

    @mock.patch('authentication.tasks.SendEmailConfirmEmailTask.delay')
    @mock.patch('social.backends.facebook.FacebookOAuth2.get_json')
    def test_signup_username_already_exists(self, get_json, delay):
        StudentFactory(user__username='geralt.derivia')
        user_counter = User.objects.count()

        get_json.return_value = {
            'email': 'derivia@witcher.com',
            'first_name': 'Geralt',
            'last_name': 'De Rivia',
            'gender': 'male',
            'id': '123456789',
            'link': 'https://www.facebook.com/app_scoped_user_id/123456789',
            'locale': 'en_US',
            'name': 'Geralt De Rivia',
            'timezone': -5,
            'verified': True,
        }

        response = self.client.post(self.url, data={
            'access_token': 'CAAYLX4HwZA38BAGjNLbUWhkBZBFR0HSDn9criXoxNUzjT'})

        student = Student.objects.last()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), user_counter + 1)
        self.assertEqual(student.user.username, 'geralt.derivia2')

    def test_validate_access_token_required(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'The access_token parameter is required'})


class ChangePasswordViewTest(BaseAPITestCase):

    def setUp(self):
        super(ChangePasswordViewTest, self).setUp()

        self.student.user.set_password('rWF&jmlc_g')
        self.student.user.save(update_fields=['password'])

        self.organizer.user.set_password('Ta0sFFetV1')
        self.organizer.user.save(update_fields=['password'])

        self.url = reverse('auth:change_password')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_change_password(self, send_mail):
        # Anonymous should get 401
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Organizer should be allowed to change the password
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.organizer.user.email,
            'status': 'sent',
            'reject_reason': None
        }]
        data = {
            'password': 'Ta0sFFetV1',
            'password1': '36o4dFi6Rt',
            'password2': '36o4dFi6Rt',
        }
        response = self.organizer_client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.organizer.user.check_password('36o4dFi6Rt'))
        self.assertTrue(EmailTaskRecord.objects.filter(
            to=self.organizer.user.email,
            status='sent').exists())

        # Student should be allowed to change the password
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.student.user.email,
            'status': 'sent',
            'reject_reason': None
        }]
        data = {
            'password': 'rWF&jmlc_g',
            'password1': 'hMTq8Re7Xv',
            'password2': 'hMTq8Re7Xv',
        }
        response = self.student_client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.student.user.check_password('hMTq8Re7Xv'))
        self.assertTrue(EmailTaskRecord.objects.filter(
            to=self.student.user.email,
            status='sent').exists())

class ForgotPasswordViewTest(BaseAPITestCase):

    def setUp(self):
        super(ForgotPasswordViewTest, self).setUp()
        self.url = reverse('auth:forgot_password')

        self.user = UserFactory(email='drake.nathan@uncharted.com')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_forgot_password(self, send_mail):
        # Anonymous should be allowed to ask for new password
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]
        response = self.client.post(self.url, data={'email': self.user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(EmailTaskRecord.objects.filter(
            to=self.user.email,
            status='sent').exists())

        # Student should not be allowed
        response = self.student_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Organizer should not be allowed
        response = self.organizer_client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_validate_email(self):
        response = self.client.post(self.url, data={'email': 'invalid@email.com'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'email': ['Este correo no existe']})

    @mock.patch('authentication.tasks.SendEmailResetPasswordTask.delay')
    def test_invalidate_pending_token(self, task_delay):
        reset_password = ResetPasswordToken.objects.create(user=self.user)
        self.client.post(self.url, data={'email': 'drake.nathan@uncharted.com'})
        self.assertFalse(ResetPasswordToken.objects.filter(id=reset_password.id).exists())
        self.assertEqual(ResetPasswordToken.objects.filter(user=self.user).count(), 1)


class ResetPasswordViewTest(APITestCase):

    def setUp(self):
        self.user = UserFactory(password='8LmmlZn@JD')
        self.reset_password = ResetPasswordToken.objects.create(
            user=self.user,
            token='5da256d75377d67e770d83247ca1d538c182c814')
        self.url = reverse('auth:reset_password')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_reset_password(self, send_mail):
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.user.email,
            'status': 'sent',
            'reject_reason': None
        }]

        data = {
            'token': self.reset_password.token,
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        user = User.objects.get(id=self.user.id)
        reset_password = ResetPasswordToken.objects.get(id=self.reset_password.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password('3jHZGtfqAS'))
        self.assertTrue(reset_password.used)
        self.assertTrue(EmailTaskRecord.objects.filter(
            to=self.user.email,
            status='sent').exists())

    def test_validate_token_key(self):
        data = {
            'token': '1c77d52e79d1b3d11a07f8423e71f2ecc41bff53',
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])

    def test_validate_token_date(self):
        reset_password = ResetPasswordToken.objects.create(user=self.user, valid_until=now())
        data = {
            'token': reset_password.token,
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])

    def test_validate_token_used(self):
        reset_password = ResetPasswordToken.objects.create(user=self.user, used=True)
        data = {
            'token': reset_password.token,
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])

    def test_validate_password(self):
        data = {
            'token': self.reset_password.token,
            'password1': '3jHZGtfqAS',
            'password2': 'SAqftGZHj3',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Las contraseñas no son iguales.'])


class ConfirmEmailViewTest(APITestCase):

    def setUp(self):
        self.url = reverse('auth:confirm_email')
        self.student = StudentFactory(user__email='derivia@witcher.com')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_confirm_email(self, send_mail):
        send_mail.return_value = [{
            'email': 'drake.nathan@uncharted.com',
            'status': 'sent',
            'reject_reason': None,
        }]

        confirm_email = ConfirmEmailToken.objects.create(
            user=self.student.user,
            email='drake.nathan@uncharted.com')
        data = {
            'token': confirm_email.token,
        }
        response = self.client.post(self.url, data=data)
        student = Student.objects.get(id=self.student.id)
        confirm_email = ConfirmEmailToken.objects.get(id=confirm_email.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, StudentsSerializer(student).data)
        self.assertEqual(student.user.email, 'drake.nathan@uncharted.com')
        self.assertTrue(student.verified_email)
        self.assertTrue(confirm_email.used)

    def test_validate_token_key(self):
        data = {
            'token': '1c77d52e79d1b3d11a07f8423e71f2ecc41bff53',
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])

    def test_validate_token_date(self):
        confirm_email = ConfirmEmailToken.objects.create(
            user=self.student.user, valid_until=now())
        data = {
            'token': confirm_email.token,
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])

    def test_validate_token_used(self):
        confirm_email = ConfirmEmailToken.objects.create(user=self.student.user, used=True)
        data = {
            'token': confirm_email.token,
            'password1': '3jHZGtfqAS',
            'password2': '3jHZGtfqAS',
        }
        response = self.client.post(self.url, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])


class ChangeEmailViewTest(BaseAPITestCase):

    def setUp(self):
        super(ChangeEmailViewTest, self).setUp()
        self.url = reverse('auth:change_email')

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_change_email(self, send_mail):
        # Anonymous should get unauthorized
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Student should change the email
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'kratos@godofwar.com',
            'status': 'sent',
            'reject_reason': None
        }]
        response = self.student_client.post(self.url, data={'email': 'kratos@godofwar.com'})
        student = Student.objects.get(id=self.student.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(student.verified_email)
        self.assertTrue(EmailTaskRecord.objects.filter(
            to='kratos@godofwar.com',
            status='sent').exists())

        # Organizer should change the email
        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': 'aiden.pearce@watchdogs.com',
            'status': 'sent',
            'reject_reason': None
        }]
        response = self.organizer_client.post(
            self.url, data={'email': 'aiden.pearce@watchdogs.com'})
        organizer = Organizer.objects.get(id=self.organizer.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(organizer.verified_email)
        self.assertTrue(EmailTaskRecord.objects.filter(
            to='aiden.pearce@watchdogs.com',
            status='sent').exists())

    @mock.patch('authentication.tasks.SendEmailConfirmEmailTask.delay')
    def test_invalidate_pending_token(self, task_delay):
        confirm_email = ConfirmEmailToken.objects.create(user=self.student.user)
        self.student_client.post(self.url, data={'email': 'drake.nathan@uncharted.com'})
        self.assertFalse(ConfirmEmailToken.objects.filter(id=confirm_email.id).exists())
        self.assertEqual(ConfirmEmailToken.objects.filter(user=self.student.user).count(), 1)


class VerifyConfirmEmailTokenViewTest(APITestCase):

    def test_valid(self):
        confirm_email = ConfirmEmailToken.objects.create(user=UserFactory())
        url = reverse('auth:verify_email_token', args=(confirm_email.token,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid(self):
        url = reverse('auth:verify_email_token', args=('1nv4l1dt0k3n',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])


class VerifyResetPasswordTokenViewTest(APITestCase):

    def test_valid(self):
        reset_password = ResetPasswordToken.objects.create(user=UserFactory())
        url = reverse('auth:verify_password_token', args=(reset_password.token,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid(self):
        url = reverse('auth:verify_password_token', args=('1nv4l1dt0k3n',))
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, ['Este token no es válido.'])


class RequestSignupTestView(BaseAPITestCase):
    """
    Testing cases for RequestSignup
    """

    def setUp(self):
        # URL
        self.create_url = reverse('auth:request_signup')

        self.city = mommy.make(City, point='POINT(1 2)')
        self.data = {
            'name': 'Organizador',
            'email': 'organizer@testing.com',
            'telephone': '987654321',
            'city': self.city.id,
            'document_type': 'cc',
            'document': '123456789',
            'approved': True,
        }

    def test_create(self):
        """
        Create an instance request_signup
        """

        request_counter = RequestSignup.objects.count()

        # Anonymous should create the request
        response = self.client.post(self.create_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RequestSignup.objects.count(), request_counter + 1)
        self.assertTrue(RequestSignup.objects.filter(**{
            **self.data, 'city': self.city, 'approved': False}).exists())

    def test_validate_if_email_exists(self):
        """
        Validate if an organizer has that email
        If it has then raise a ValidationError
        """

        OrganizerFactory(user__email='organizer@testing.com')
        response = self.client.post(self.create_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
