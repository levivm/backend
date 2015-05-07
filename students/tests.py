import json
from utils.tests import BaseViewTest


class StudentViewTest(BaseViewTest):
    url = '/api/students/1'
    view_name = 'students.views.StudentViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_methods_for_anonymous(self):
        self.method_get_should_return_data(clients=self.client)
        self.authorization_should_be_require()

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='put', status=403)
        self.method_should_be(clients=organizer, method='delete', status=403)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_student_should_update(self):
        student = self.get_student_client()
        data = json.dumps({ 'gender': 1 })
        response = student.put(self.url, data=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"gender":1', response.content)

    def test_another_student_shouldnt_update(self):
        student = self.get_student_client(user_id=4)
        self.method_should_be(clients=student, method='put', status=403)
