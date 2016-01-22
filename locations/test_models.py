from rest_framework.test import APITestCase

from locations.factories import LocationFactory
from organizers.factories import OrganizerFactory


class LocationTestCase(APITestCase):

    def setUp(self):
        self.organizer = OrganizerFactory()
        self.location = LocationFactory(organizer=self.organizer)

    def test_permissions(self):
        user = self.location.organizer.user
        self.assertTrue(user.has_perm('locations.change_location', self.location))
        self.assertTrue(user.has_perm('locations.add_location', self.location))
        self.assertTrue(user.has_perm('locations.delete_location', self.location))
