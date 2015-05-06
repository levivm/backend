from utils.tests import BaseViewTest


class OrdersByActivityViewTest(BaseViewTest):
    url = '/api/activities/1/orders'
    view_name = 'orders.views.OrdersViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=403)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_students_should_create_an_order(self):
        client = self.get_student_client()
        data = {
            'chronogram': 1,
            'amount': 324000,
            'quantity': 1,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }
        response = client.post(self.url, data)
        self.assertEqual(response.status_code, 201)
        self.assertIn(b'"id":2', response.content)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='put', status=403)
        self.method_should_be(clients=organizer, method='delete', status=403)

    def test_another_organizer_shouldnt_get_the_order(self):
        organizer = self.get_organizer_client(user_id=2)
        self.method_should_be(clients=organizer, method='get', status=404)


class GetSingleOrderViewTest(BaseViewTest):
    url = '/api/orders/1'
    view_name = 'orders.views.OrdersViewSet'
    another_student_id = 4

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_authorization_should_be_require(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=405)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=403)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='put', status=403)
        self.method_should_be(clients=organizer, method='delete', status=403)

    def test_another_student_shouldnt_get_the_order(self):
        student = self.get_student_client(user_id=4)
        self.method_should_be(clients=student, method='get', status=404)


class ByStudentViewTest(BaseViewTest):
    url = '/api/students/1/orders'
    view_name = 'orders.views.OrdersViewSet'

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly(self.url, self.view_name)

    def test_authorization_should_be_require(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=403)
        self.method_should_be(clients=organizer, method='post', status=403)
        self.method_should_be(clients=organizer, method='put', status=403)
        self.method_should_be(clients=organizer, method='delete', status=403)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=405)
        self.method_should_be(clients=student, method='put', status=403)
        self.method_should_be(clients=student, method='delete', status=403)
