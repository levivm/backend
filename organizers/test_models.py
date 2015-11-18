from model_mommy import mommy
from rest_framework.test import APITestCase

from organizers.models import OrganizerBankInfo


class OrganizerBankInfoModelTest(APITestCase):
    """
    Test for OrganizerBankInfo model
    """

    def setUp(self):
        self.bank_info = mommy.make(OrganizerBankInfo)

    def test_get_choices(self):
        """
        Test method get_choices
        """

        data = {
            'banks': [{'bank_id': k, 'bank_name': v} for k, v in OrganizerBankInfo.BANKS],
            'documents': [{'document_id': k, 'document_name': v} for k, v in OrganizerBankInfo.DOCUMENT_TYPES],
            'accounts': [{'account_id': k, 'account_name': v} for k, v in OrganizerBankInfo.ACCOUNT_TYPES],
        }

        self.assertTrue(all(item in self.bank_info.get_choices().items() for item in data.items()))
