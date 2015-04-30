from django.contrib.auth.models import User
from django.core.urlresolvers import resolve

# Un usuario anonimo no puede traer nada
# Un organizador no puede traer nada
# Revisar que sea un estudiante
# Estudiante no owner no puede traer nada
# Traer las ordenes
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient


class BaseOrdersViewTest(APITestCase):
    fixtures = ['orders_testdata.json', 'students_testdata.json', 'activities_testdata.json',
                'organizers_testdata.json', 'users_testdata.json', 'groups_testdata.json']
    url = None
    view_name = 'orders.views.OrdersViewSet'
    __organizer_id = 1
    __student_id = 3

    def __get_token(self, user_id):
        user = User.objects.get(id=user_id)
        token = Token.objects.create(user=user)
        return token

    def __get_client_with_credentials(self, token):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % token.key)
        return client

    def get_organizer_client(self, user_id=None):
        user_id = user_id or self.__organizer_id
        token = self.__get_token(user_id=user_id)
        return self.__get_client_with_credentials(token=token)

    def get_student_client(self, user_id=None):
        user_id = user_id or self.__student_id
        token = self.__get_token(user_id=user_id)
        return self.__get_client_with_credentials(token=token)


class CreateOrdersViewTest(BaseOrdersViewTest):
    url = '/api/activities/1/orders'

    def test_students_can_create_an_order(self):
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

    def test_organizers_cant_create_orders(self):
        client = self.get_organizer_client()
        response = client.post(self.url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cant_create_orders(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 401)


class OrdersByActivityViewTest(BaseOrdersViewTest):
    url = '/api/activities/1/orders'

    def test_url_resolve_to_view_correctly(self):
        found = resolve(self.url)
        self.assertEqual(found.view_name, self.view_name)

    def test_view_returns_correct_response_to_organizer(self):
        client = self.get_organizer_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"id":1', response.content)

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_students_shouldnt_get_orders(self):
        client = self.get_student_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)


class GetSingleOrderViewTest(BaseOrdersViewTest):
    url = '/api/orders/1'
    another_student_id = 4

    def test_url_resolve_to_view_correctly(self):
        found = resolve(self.url)
        self.assertEqual(found.view_name, self.view_name)

    def test_anonymous_shouldnt_get_an_order(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_student_owner_should_get_the_order(self):
        client = self.get_student_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"id":1', response.content)

    def test_student_not_owner_shouldnt_get_the_order(self):
        client = self.get_student_client(user_id=self.another_student_id)
        response = client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_organizer_shouldnt_get_the_order(self):
        client = self.get_organizer_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)


class OrdersByStudentViewTest(BaseOrdersViewTest):
    url = '/api/students/1/orders'

    def test_url_resolve_to_view_correctly(self):
        found = resolve(self.url)
        self.assertEqual(found.view_name, self.view_name)

    def test_view_returns_correct_response_to_student(self):
        client = self.get_student_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'"id":1', response.content)

    def test_anonymous_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 401)

    def test_organizers_shouldnt_get_orders(self):
        client = self.get_organizer_client()
        response = client.get(self.url)
        self.assertEqual(response.status_code, 404)
