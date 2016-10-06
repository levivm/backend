from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from locations.factories import CityFactory
from users.factories import UserFactory
from users.models import RequestSignup
from users.serializers import RequestSignUpSerializer


class RequestSignUpSerializerTest(APITestCase):
    """
    Testing class for RequestSignUpSerializer
    """
    def setUp(self):
        self.city = CityFactory()

    def test_create(self):
        """
        Test create a RequestSignUp instance
        """
        data = {
            'email': 'big.boss@example.com',
            'name': 'Diamond Dogs',
            'telephone': '+98(8)0832533372',
            'city': self.city.id,
            'document_type': 'nit',
            'document': '496-81-7893',
        }

        serializer = RequestSignUpSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(RequestSignup.objects.filter(
            email=data['email'],
            name=data['name']).exists())

    def test_validate_email(self):
        """
        Validate that the email doesn't already exists
        """
        UserFactory(email='big.boss@example.com')

        data = {
            'email': 'big.boss@example.com',
            'name': 'Diamond Dogs',
            'telephone': '+98(8)0832533372',
            'city': self.city.id,
            'document_type': 'nit',
            'document': '496-81-7893',
        }

        serializer = RequestSignUpSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, 'Este correo ya existe.'):
            serializer.is_valid(raise_exception=True)

    def test_validate_email_upper_case(self):
        UserFactory(email='big.boss@example.com')

        data = {
            'email': 'Big.Boss@example.com',
            'name': 'Diamond Dogs',
            'telephone': '+98(8)0832533372',
            'city': self.city.id,
            'document_type': 'nit',
            'document': '496-81-7893',
        }

        serializer = RequestSignUpSerializer(data=data)
        with self.assertRaisesMessage(ValidationError, 'Este correo ya existe.'):
            serializer.is_valid(raise_exception=True)
