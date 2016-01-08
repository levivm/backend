import statistics
from itertools import cycle

from model_mommy import mommy
from rest_framework.test import APITestCase

from activities.models import Activity
from organizers.factories import OrganizerFactory, InstructorFactory
from organizers.models import OrganizerBankInfo, Organizer
from reviews.models import Review


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


class OrganizerModelTest(APITestCase):
    """
    Class for testing the model Organizer
    """

    def setUp(self):
        self.organizer = mommy.make(Organizer)
        self.activities = mommy.make(Activity, organizer=self.organizer, _quantity=2)

    def test_update_rating(self):
        """
        Test to calculate the rating of the organizer
        """

        self.assertEqual(self.organizer.rating, 0)

        reviews = mommy.make(Review, activity=cycle(self.activities), rating=cycle([2,3,4,4]), _quantity=4)
        average = statistics.mean([r.rating for r in reviews])
        self.assertEqual(self.organizer.rating, average)

        # Delete a review
        reviews.pop().delete()
        average = statistics.mean([r.rating for r in reviews])
        self.assertEqual(self.organizer.rating, average)


class InstructorModelTest(APITestCase):
    """
    Class for testing the model Instructor
    """

    def setUp(self):
        self.organizer = OrganizerFactory()
        self.instructor = InstructorFactory(organizer=self.organizer)

    def test_permissions(self):
        user = self.organizer.user
        self.assertTrue(user.has_perm('organizers.change_instructor', self.instructor))
        self.assertTrue(user.has_perm('organizers.delete_instructor', self.instructor))
