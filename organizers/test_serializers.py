from model_mommy import mommy
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from locations.serializers import LocationsSerializer
from organizers.factories import OrganizerFactory
from organizers.models import Organizer, OrganizerBankInfo
from organizers.serializers import OrganizerBankInfoSerializer, OrganizersSerializer
from users.forms import UserCreateForm
from users.serializers import UsersSerializer
from utils.serializers import UnixEpochDateField
from utils.tests import TestMixinUtils


class OrganizerBankInfoSerializerTest(APITestCase):
    """
    Class to test the OrganizerBankInfoSerializer
    """

    def setUp(self):
        # Arrangement
        self.organizer = mommy.make(Organizer)
        self.data = {
            'organizer': self.organizer.id,
            'beneficiary': 'Beneficiario',
            'bank': 'bancolombia',
            'document_type': 'cc',
            'document': '123456789',
            'account_type': 'ahorros',
            'account': '987654321-0',
        }
        self.content = self.data.copy()
        self.content['organizer_id'] = self.content.pop('organizer')

    def test_create(self):
        """
        Test create an OrganizerBankInfo
        """

        serializer = OrganizerBankInfoSerializer(data=self.data)
        serializer.is_valid(raise_exception=True)
        bank_info = serializer.save()

        self.assertTrue(OrganizerBankInfo.objects.filter(organizer=self.organizer,
                                                         beneficiary=self.data['beneficiary'])
                                                 .exists())
        self.assertTrue(all(item in bank_info.__dict__.items() for item in self.content.items()))

    def test_read(self):
        """
        Test read
        """

        self.data['organizer'] = self.organizer
        self.content['organizer'] = self.content.pop('organizer_id')

        bank_info = OrganizerBankInfo.objects.create(**self.data)
        serializer = OrganizerBankInfoSerializer(bank_info)

        self.assertTrue(all(item in serializer.data.items() for item in self.content.items()))

    def test_update(self):
        """
        Test update
        """

        self.data['organizer'] = self.organizer
        self.content['organizer'] = self.content.pop('organizer_id')
        bank_info = OrganizerBankInfo.objects.create(**self.data)

        update_data = {
            'beneficiary': 'Harvey',
            'account': 'corriente',
            'bank': 'helmbank',
        }

        serializer = OrganizerBankInfoSerializer(bank_info, data=update_data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        self.assertTrue(
            OrganizerBankInfo.objects.filter(organizer=self.organizer, **update_data).exists())

    def test_validation_all_fields_required(self):
        """
        Test to validate that all fields are required
        """

        del self.data['account']

        with self.assertRaises(ValidationError):
            serializer = OrganizerBankInfoSerializer(data=self.data)
            serializer.is_valid(raise_exception=True)


class OrganizerSerialiezerTest(TestMixinUtils, APITestCase):
    """
    Test the OrganizerSerializer
    """

    def setUp(self):
        self.organizer = OrganizerFactory()

    def test_read(self):
        """
        Test the serializer's data
        """

        user_data = UsersSerializer(self.organizer.user).data
        created_at = UnixEpochDateField().to_representation(self.organizer.created_at)

        content = {
            'id': self.organizer.id,
            'user': user_data,
            'name': self.organizer.name,
            'bio': self.organizer.bio,
            'headline': self.organizer.headline,
            'website': self.organizer.website,
            'youtube_video_url': self.organizer.youtube_video_url,
            'telephone': self.organizer.telephone,
            'photo': None,
            'user_type': UserCreateForm.USER_TYPES[0][0],
            'created_at': created_at,
            'instructors': [],
            'locations': LocationsSerializer(self.organizer.locations.all(), many=True).data,
            'rating': self.organizer.rating,
            'verified_email': self.organizer.verified_email,
        }

        serializer = OrganizersSerializer(self.organizer)
        self.assertTrue(all(item in serializer.data.items() for item in content.items()),
                        self.all_serializer_items_diff_assertion(serializer, content))
