import json
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import resolve
from model_mommy import mommy
from requests import post

from organizers.factories import OrganizerFactory
from payments.models import Payment
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from students.factories import StudentFactory


class BaseViewTest(APITestCase):
    fixtures = ['orders_testdata', 'students_testdata', 'activities_testdata', 'organizers_testdata', 'users_testdata',
                'groups_testdata', 'object_permissions_testdata', 'instructors_testdata', 'locations_testdata',
                'payments_testdata', 'reviews_testdata']
    url = None
    view = None
    ORGANIZER_ID = 1
    ANOTHER_ORGANIZER_ID = 2
    STUDENT_ID = 3
    ADMIN_ID   = 5
    ANOTHER_STUDENT_ID = 4
    DUMMY_PASSWORD = 'password'
    __SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']
    headers = { 'content_type': 'application/json' }

    def __get_token(self, user_id):
        user = User.objects.get(id=user_id)
        token, created = Token.objects.get_or_create(user=user)
        return token

    def __get_client_with_credentials(self, token):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token %s' % token.key)
        return client

    def __get_admin_client_logged_in(self,admin_user):
        admin_user.set_password(self.DUMMY_PASSWORD)
        admin_user.save()
        client = self.client
        client.login(username=admin_user.username,password=self.DUMMY_PASSWORD)
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

    def get_admin_client(self):
        admin_id = self.ADMIN_ID
        admin = User.objects.get(id=admin_id)
        return self.__get_admin_client_logged_in(admin)

    def url_resolve_to_view_correctly(self):
        found = resolve(self.url)
        self.assertEqual(found.func.__name__, self.view.__name__)

    def method_should_be(self, clients, method, status, **params):
        clients = self.__parse_clientes(clients=clients)

        for client in clients:
            client_method = getattr(client, method.lower())
            response = client_method(self.url, **params)
            self.assertEqual(response.status_code, status)

    def method_get_should_return_data(self, clients, data=None, response_data=None):
        response_data = response_data or b'"id":1'
        clients = self.__parse_clientes(clients=clients)

        for client in clients:
            response = client.get(self.url, data)
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

    def get_token(self):
        data = {
            'language': 'es',
            'command': 'CREATE_TOKEN',
            'merchant': {
              'apiLogin': settings.PAYU_API_LOGIN,
              'apiKey': settings.PAYU_API_KEY,
            },
            'creditCardToken': {
                'payerId': self.STUDENT_ID,
                'number': '4111111111111111',
                'expirationDate': '2018/08',
                'name': 'test',
                'paymentMethod': 'VISA',
            },
        }
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        result = post(url=settings.PAYU_URL, data=json.dumps(data), headers=headers)
        result = result.json()
        try:
            token = result['creditCardToken']['creditCardTokenId']
        except:
            raise Exception('Missing token', result)
        return token

    def get_payment_data(self):
        return {
            'token': self.get_token(),
            'buyer': {
                'name': 'APPROVED',
                'email': 'test@payulatam.com',
            },
            'last_four_digits':'1111',
            'card_association': 'visa',
            'calendar': 1,
            'payment_method':Payment.CC_PAYMENT_TYPE,
            'quantity': 1,
            'amount': 324000,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }

    def get_buyer_pse_data(self):
        return {
             "response_url": settings.PAYU_RESPONSE_URL,
             "bank": "1007",
             "userType": "J",
             "idType": "NIT",
             "idNumber": "900823805",
        }

    def get_payment_pse_data(self):
        return {
            'buyer': {
                'name': 'PENDING',
                'payerEmail': 'levi@trulii.com',
                 'contactPhone':"222222"

            },
            'buyer_pse_data':self.get_buyer_pse_data(),
            'calendar': 1,
            'activity':1,
            'payment_method':Payment.PSE_PAYMENT_TYPE,
            'quantity': 1,
            'amount': 8000,
            'assistants': [{
                'first_name': 'Asistente',
                'last_name': 'Asistente',
                'email': 'asistente@trulii.com',
            }]
        }

class BaseAPITestCase(APITestCase):
    """
    Base class to initialize the test cases
    """

    def setUp(self):
        # Users
        self.student, self.another_student = StudentFactory.create_batch(2)
        self.organizer, self.another_organizer = OrganizerFactory.create_batch(2)

        # API Clients
        self.student_client = self.get_client(user=self.student.user)
        self.organizer_client = self.get_client(user=self.organizer.user)
        self.another_student_client = self.get_client(user=self.another_student.user)
        self.another_organizer_client = self.get_client(user=self.another_organizer.user)

    def get_client(self, user):
        """
        Authenticate a user and return the client
        """
        token = mommy.make(Token, user=user)
        client = APIClient()
        client.force_authenticate(user=user, token=token)
        return client


class TestMixinUtils(object):
    """
    Some method to help the test
    """

    def all_serializer_items_diff_assertion(self, serializer, content):
        "Find out the different items and print them out"
        for item in content.items():
            if item not in serializer.data.items():
                key, val = item
                print('CONTENT %s' % key.upper(), val)
                print('SERIALIZER %s' % key.upper(), serializer.data[key])

    def diff_between_lists(self, list_a, list_b):
        """
        Find the different items between two lists
        :type list_a: list
        :type list_b: list
        """

        diff = (item for item in list_a if item not in list_b)
        for d in diff:
            print(d)
