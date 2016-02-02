from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from authentication.serializers import AuthTokenSerializer
from users.factories import UserFactory


class AuthTokenSerializerTest(APITestCase):
    """
    Class for test AuthTokenSerializer
    """

    def setUp(self):
        self.password = 'MlRdoAPzfe'
        self.user = UserFactory()
        self.user.set_password(self.password)
        self.user.save()

    def validate_user_success(self):
        """
        Validate user successful
        """
        data = {
            'email': self.user.email,
            'password': self.password,
        }

        serializer = AuthTokenSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data['user'], self.user)

    def validate_user_inactive(self):
        """
        Validate an inactive user
        """
        self.user.is_active = False
        self.user.save()

        data = {
            'email': self.user.email,
            'password': self.password,
        }

        serializer = AuthTokenSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def validate_user_wrong_password(self):
        """
        Validate a user with wrong password
        """
        self.user.is_active = False
        self.user.save()

        data = {
            'email': self.user.email,
            'password': 'qwerty',
        }

        serializer = AuthTokenSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def validate_user_missig_data(self):
        """
        Validate with missing data
        """
        self.user.is_active = False
        self.user.save()

        data = {
            'email': self.user.email,
        }

        serializer = AuthTokenSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
