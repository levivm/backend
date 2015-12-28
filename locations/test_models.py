from rest_framework.test import APITestCase

from locations.factories import LocationFactory


class LocationTestCase(APITestCase):

    def setUp(self):
        self.location = LocationFactory()

    def test_permissions(self):
        user = self.location.organizer.user
        self.assertTrue(user.has_perm('locations.change_location', self.location))
        self.assertTrue(user.has_perm('locations.add_location', self.location))
        self.assertTrue(user.has_perm('locations.delete_location', self.location))
