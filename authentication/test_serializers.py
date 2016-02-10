from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from authentication.serializers import AuthTokenSerializer, SignUpStudentSerializer
from users.factories import UserFactory


class AuthTokenSerializerTest(APITestCase):
    """
    Class for test AuthTokenSerializer
    """

    def setUp(self):
        self.password = 'MlRdoAPzfe'
        self.user = UserFactory(password=self.password)

    def test_validate_user_success(self):
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

    def test_validate_user_inactive(self):
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

    def test_validate_user_wrong_password(self):
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

    def test_validate_user_missig_data(self):
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


class SignUpStudentSerializerTest(APITestCase):
    """
    Test cases for SignUpStudentSerializer
    """

    def test_all_fields_required(self):
        """
        Test all fields are required
        """
        data = {}
        exceptions = [
            'email',
            'first_name',
            'last_name',
            'password1',
        ]

        serializer = SignUpStudentSerializer(data=data)

        for exception in exceptions:
            message = "'%s': ['Este campo es requerido.']" % exception
            with self.assertRaisesMessage(ValidationError, message):
                serializer.is_valid(raise_exception=True)

    def test_validate_unique_email(self):
        """
        Test the email is unique
        """
        UserFactory(email='jack.bauer@example.com')
        data = {
            'email': 'jack.bauer@example.com',
            'first_name': 'Jack',
            'last_name': 'Bauer',
            'password1': 'jackisthebest',
            'user_type': 'S',
        }

        serializer = SignUpStudentSerializer(data=data)

        message = "A user is already registered with this e-mail address."
        with self.assertRaisesMessage(ValidationError, message):
            serializer.is_valid(raise_exception=True)

    def test_generate_username(self):
        """
        Test the username generation
        """
        data = {
            'email': 'jack.bauer@example.com',
            'first_name': 'Jack',
            'last_name': 'Bauer',
            'password1': 'jackisthebest',
            'user_type': 'S',
        }

        serializer = SignUpStudentSerializer(data=data)
        serializer.is_valid(raise_exception=True)

        self.assertEqual(serializer.validated_data['username'], 'jack.bauer')
