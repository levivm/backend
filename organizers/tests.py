import json
from rest_framework import status
from organizers.views import OrganizerViewSet, InstructorViewSet
from utils.tests import BaseViewTest


class OrganizerViewTest(BaseViewTest):
    url = '/api/organizers/1'
    view = OrganizerViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_organizer_should_edit_own_organizer(self):
        client = self.get_organizer_client()
        data = json.dumps({ "name": "Another Name" })
        response = client.put(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b'"name":"Another Name"', response.content)

    def test_organizer_shouldnt_edit_another_organizer(self):
        client = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        data = json.dumps({ "name": "Second Organizer" })
        response = client.put(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrganizerActivitiesViewTest(BaseViewTest):
    url = '/api/organizers/1/activities'
    view = OrganizerViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)


class OrganizersInstructorsViewTest(BaseViewTest):
    url = '/api/organizers/1/instructors/1'
    view = InstructorViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_organizer_should_delete_an_instructor(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_204_NO_CONTENT)
