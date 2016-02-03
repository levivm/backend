import mock
import json
import urllib

from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from organizers.factories import OrganizerFactory
from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.factories import StudentFactory
from students.models import Student
from students.serializer import StudentsSerializer
from users.factories import RequestSignUpFactory


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

    def test_student_signup_success(self):
        """
        Test case success for a student sign up
        """
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

    def test_validate_password(self):
        """
        Test the password is required
        """
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'password': ['The password is required.']})

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
