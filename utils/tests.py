from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient


class BaseViewTest(APITestCase):
    fixtures = ['orders_testdata', 'students_testdata', 'activities_testdata', 'organizers_testdata', 'users_testdata',
                'groups_testdata', 'object_permissions_testdata', 'instructors_testdata']
    url = None
    view = None
    ORGANIZER_ID = 1
    ANOTHER_ORGANIZER_ID = 2
    STUDENT_ID = 3
    ANOTHER_STUDENT_ID = 4
    __SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def __get_token(self, user_id):
        user = User.objects.get(id=user_id)
        token, created = Token.objects.get_or_create(user=user)
        return token

    def __get_client_with_credentials(self, token):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % token.key)
        return client

    def  __parse_clientes(self, clients):
        if not isinstance(clients, list):
            clients = [clients]

        return clients

    def get_organizer_client(self, user_id=None):
        user_id = user_id or self.ORGANIZER_ID
        token = self.__get_token(user_id=user_id)
        return self.__get_client_with_credentials(token=token)

    def get_student_client(self, user_id=None):
        user_id = user_id or self.STUDENT_ID
        token = self.__get_token(user_id=user_id)
        return self.__get_client_with_credentials(token=token)

    def url_resolve_to_view_correctly(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def method_should_be(self, clients, method, status, **params):
        clients = self.__parse_clientes(clients=clients)

        for client in clients:
            client_method = getattr(client, method.lower())
            response = client_method(self.url, params)
            self.assertEqual(response.status_code, status)

    def method_get_should_return_data(self, clients, response_data=None):
        response_data = response_data or b'"id":1'
        clients = self.__parse_clientes(clients=clients)

        for client in clients:
            response = client.get(self.url)
            self.assertEqual(response.status_code, 200)
            self.assertIn(response_data, response.content)

    def authorization_should_be_require(self, safe_methods=False):
        methods = ['POST', 'PUT', 'DELETE']

        if safe_methods:
            methods += self.__SAFE_METHODS

        for method in methods:
            client_method = getattr(self.client, method.lower())
            response = client_method(self.url)
            self.assertEqual(response.status_code, 401)