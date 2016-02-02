import json

from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from students.factories import StudentFactory
from students.serializer import StudentsSerializer


class LoginViewTest(APITestCase):
    """
    Tests for LoginView
    """

    def setUp(self):
        self.student = StudentFactory()
        self.password = '12345678'
        self.student.user.set_password(self.password)
        self.student.user.save()
        self.token = Token.objects.create(user=self.student.user)

        self.url = reverse('auth:login')

    def test_login_success(self):
        """
        Test login success
        """

        data = {
            'email': self.student.user.email,
            'password': self.password,
        }

        content = {
            'user': StudentsSerializer(self.student).data,
            'token': self.token.key,
        }

        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, content)
