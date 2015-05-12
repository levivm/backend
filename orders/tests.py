from rest_framework import status
from orders.models import Order
from orders.views import OrdersViewSet
from utils.tests import BaseViewTest


class OrdersByActivityViewTest(BaseViewTest):
    url = '/api/activities/1/orders'
    view = OrdersViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_methods_for_anonymous(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_should_be(clients=student, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

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
        order = Order.objects.latest('pk')
        expected = bytes('"id":%s' % order.id, 'utf8')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn(expected, response.content)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_get_should_return_data(clients=organizer)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_another_organizer_shouldnt_get_the_order(self):
        organizer = self.get_organizer_client(user_id=self.ANOTHER_ORGANIZER_ID)
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_404_NOT_FOUND)


class GetSingleOrderViewTest(BaseViewTest):
    url = '/api/orders/1'
    view = OrdersViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_authorization_should_be_require(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_another_student_shouldnt_get_the_order(self):
        student = self.get_student_client(user_id=self.ANOTHER_STUDENT_ID)
        self.method_should_be(clients=student, method='get', status=status.HTTP_404_NOT_FOUND)


class ByStudentViewTest(BaseViewTest):
    url = '/api/students/1/orders'
    view = OrdersViewSet

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_authorization_should_be_require(self):
        self.authorization_should_be_require(safe_methods=True)

    def test_methods_for_organizer(self):
        organizer = self.get_organizer_client()
        self.method_should_be(clients=organizer, method='get', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='post', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=organizer, method='delete', status=status.HTTP_403_FORBIDDEN)

    def test_methods_for_student(self):
        student = self.get_student_client()
        self.method_get_should_return_data(clients=student)
        self.method_should_be(clients=student, method='post', status=status.HTTP_405_METHOD_NOT_ALLOWED)
        self.method_should_be(clients=student, method='put', status=status.HTTP_403_FORBIDDEN)
        self.method_should_be(clients=student, method='delete', status=status.HTTP_403_FORBIDDEN)