import json
from utils.tests import BaseViewTest


class OrganizerViewTest(BaseViewTest):
    url = '/api/organizers/1'
    view_name = 'organizers.views.OrganizerViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=403)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='delete', status=403)

    def test_organizer_should_edit_own_organizer(self):
        client = self.get_organizer_client()
        data = json.dumps({ "name": "Another Name" })
        response = client.put(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"name":"Another Name"', response.content)

    def test_organizer_shouldnt_edit_another_organizer(self):
        client = self.get_organizer_client(user_id=2)
        data = json.dumps({ "name": "Second Organizer" })
        response = client.put(self.url, data, content_type='application/json')
        self.assertEqual(response.status_code, 403)


class OrganizerActivitiesViewTest(BaseViewTest):
    url = '/api/organizers/1/activities'
    view_name = 'organizers.views.OrganizerViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=403)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='put', status=405)
        self.method_should_be(clients=organizer, method='delete', status=403)


class OrganizersInstructorsViewTest(BaseViewTest):
    url = '/api/organizers/1/instructors/1'
    view_name = 'organizers.views.InstructorViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=405)
        self.method_should_be(clients=student, method='post', status=403)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=405)
        self.method_should_be(clients=organizer, method='post', status=405)
        self.method_should_be(clients=organizer, method='put', status=405)

    def test_organizer_should_delete_an_instructor(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='delete', status=204)
