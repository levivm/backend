import json

import mock
# from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import loader
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from locations.factories import CityFactory
from locations.models import City
# from users.allauth_adapter import MyAccountAdapter
from users.models import OrganizerConfirmation
from utils.models import EmailTaskRecord
from utils.tests import BaseViewTest, BaseAPITestCase
from .models import RequestSignup
from .tasks import SendEmailOrganizerConfirmationTask  #, SendAllAuthEmailTask


# class RestFacebookLoginTest(BaseAPITestCase):
#     """
#     Class to test sign up and login with Facebook
#     """
#
#     def setUp(self):
#         super(RestFacebookLoginTest, self).setUp()
#
#         # URLs
#         self.facebook_signup_login_url = reverse('facebook_signup_login')
#
#         # Objects
#         mommy.make(SocialApp,
#                    name='trulii',
#                    client_id='1563536137193781',
#                    secret='9fecd238829796fd99109283aca7d4ff',
#                    provider='facebook',
#                    sites=[Site.objects.get(id=settings.SITE_ID)])
#
#     def get_signup_data(self):
#         # TODO
#         # Este token dura dos meses, expira en marzo
#         # Automatizar para pedir uno
#
#         auth_token = "CAAWOByANCTUBAOd9x0yTEYdAuuMUG7WvYZAzdAp4otJOi7gIsOWCnuAvNADtYqW7CW9AhF" \
#                      "6uUCIQMI975sxnAvZBU8csApZC5RHWoKmHsuqU639wSTLdBkqBpCdkqbVmmZA8" \
#                      "Hp4pJAJCCCmyZAvOUColRumTi6z22niA3ZAVzm8s4Qzdjm7BVT9tMLPZAiZCDSMZD"
#         return {'auth_token': auth_token}
#
#     def test_signup(self):
#         """
#         Test to signup with Facebook
#         """
#
#         data = self.get_signup_data()
#
#         # Anonymous should sign up
#         response = self.client.post(self.facebook_signup_login_url, data)
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
#
#     def test_login(self):
#         """
#         Test to login with Facebook
#         """
#
#         data = self.get_signup_data()
#
#         # signup
#         self.client.post(self.facebook_signup_login_url, data)
#
#         # login
#         response = self.client.post(self.facebook_signup_login_url, data)
#
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')


# class ObtainAuthTokenTestView(BaseAPITestCase):
#     """
#     Class to test sign up and login
#     """
#     urlencoded = {'content_type': 'application/x-www-form-urlencoded'}
#     jsonencoded = {'content_type': 'application/json'}
#
#     def setUp(self):
#         super(ObtainAuthTokenTestView, self).setUp()
#
#         # Objects
#         self.password = '12345678'
#         self.email = 'student@trulii.com'
#         self.student.user.set_password(self.password)
#         self.student.user.email = self.email
#         self.student.user.save()
#
#         # URLs
#         self.signup_login_url = reverse('users:signup_login')
#
#     def get_signup_data(self):
#         return {
#             'email': self.email,
#             'first_name': 'John',
#             'last_name': 'Messi',
#             'password1': self.password,
#             'user_type': 'S'
#         }

        # def get_login_data(self):
        #     return {
        #         'login': self.email,
        #         'password': self.password,
        #     }

        # def test_signup(self):
        #     """
        #     Test to sign up an user
        #     """
        #
        #     # Anonymous should sign up
        #     data = self.get_signup_data()
        #     response = self.client.post(self.signup_login_url, urllib.parse.urlencode(data), **self.urlencoded)
        #     self.assertEqual(response.status_code, status.HTTP_200_OK)
        #     self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        #     self.assertTrue(User.objects.filter(email=data['email']).exists())
        #
        # def test_login(self):
        #     """
        #     Test to login an user
        #     """
        #
        #     # Anonymous should login
        #     data = self.get_login_data()
        #     response = self.client.post(self.signup_login_url, json.dumps(data), **self.jsonencoded)
        #     self.assertContains(response, data['login'])
        #     self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')


class RequestSignupTestView(BaseAPITestCase):
    """
    Testing cases for RequestSignup
    """

    def setUp(self):
        # URL
        self.create_url = reverse('users:request_signup')

        self.city = mommy.make(City, point='POINT(1 2)')
        self.data = {
            'name': 'Organizador',
            'email': 'organizer@testing.com',
            'telephone': '987654321',
            'city': self.city.id,
            'document_type': 'cc',
            'document': '123456789',
            'approved': True,
        }

    def test_create(self):
        """
        Create an instance request_signup
        """

        request_counter = RequestSignup.objects.count()

        # Anonymous should create the request
        response = self.client.post(self.create_url, self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(RequestSignup.objects.count(), request_counter + 1)
        self.assertTrue(RequestSignup.objects.filter(**{
            **self.data, 'city': self.city, 'approved': False}).exists())


class SendEmailOrganizerConfirmationAdminActionTest(BaseViewTest):
    url = '/olympus/users/requestsignup/'
    REQUEST_SIGNUP_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def _get_send_verification_email_action_data(self):
        return {'action': 'send_verification_email',
                '_selected_action': self.REQUEST_SIGNUP_ID}

    def test_admin_send_verification_email_action(self):
        client = self.get_admin_client()
        data = self._get_send_verification_email_action_data()
        request_signup = RequestSignup.objects.get(id=self.REQUEST_SIGNUP_ID)
        self.assertFalse(request_signup.approved)
        response = client.post(self.url, data)
        request_signup = RequestSignup.objects.get(id=self.REQUEST_SIGNUP_ID)
        self.assertTrue(request_signup.approved)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class SendEmailOrganizerConfirmationTaskTest(APITestCase):
    # CONFIRMATION_ID = 1

    def setUp(self):
        self.confirmation = mommy.make(OrganizerConfirmation, requested_signup__city=CityFactory())

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_success(self, send_mail):
        """
        Test case when it's success
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
            'email': self.confirmation.requested_signup.email,
            'status': 'sent',
            'reject_reason': None
        }]

        task = SendEmailOrganizerConfirmationTask()
        task_id = task.delay(self.confirmation.id)

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.confirmation.requested_signup.email,
            status='sent').exists())

        context = {
            'activate_url': self.confirmation.get_confirmation_url(),
            'organizer': self.confirmation.requested_signup.name
        }

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template(
                'account/email/request_signup_confirmation_message.txt').render(),
            'subject': 'Crea tu cuenta y comienza a user Trulii',
            'to': [{'email': self.confirmation.requested_signup.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in context.items()],
        }

        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))


# class SendAllAuthEmailTaskTest(BaseViewTest):
#     password_reset_template_prefix = 'account/email/password_reset_key'
#     email_confirmation_template_prefix = 'account/email/email_confirmation'
#     USER_ID = 1
#
#     def setUp(self):
#         settings.CELERY_ALWAYS_EAGER = True
#
#     def tearDown(self):
#         settings.CELERY_ALWAYS_EAGER = False
#
#     def _get_reset_password_data(self):
#         pass_reset_url = 'http://localhost:8000/users/password/reset/key/4-437-597e9e6b21e5adc283b2/'
#         return {
#             'user': self.USER_ID,
#             'site': "trulii.com",
#             'password_reset_url': pass_reset_url
#         }
#
#     def _get_email_confirmation_data(self):
#         activate_url = 'http://localhost:8000/users/confirm-email/'
#         activate_url += 'kjbps8tqbmngdk1vqub8lqlgwd6hfuznkloeh8ul2gfndalyb86kn4fswslazkzv/'
#         return {
#             'user': self.USER_ID,
#             'key': 'kjbps8tqbmngdk1vqub8lqlgwd6hfuznkloeh8ul2gfndalyb86kn4fswslazkzv',
#             'activate_url': activate_url,
#             'current_site': 1
#         }
#
#     def _get_password_reset_task_data(self):
#         context = self._get_reset_password_data()
#         adapter = MyAccountAdapter()
#
#         return {
#             'account_adapter': adapter,
#             'email_data': {
#                 'template_prefix': self.password_reset_template_prefix,
#                 'email': "h@trulii.com",
#                 'context': json.dumps(context)
#             }
#
#         }
#
#     def _get_email_confirmation_task_data(self):
#         context = self._get_email_confirmation_data()
#         adapter = MyAccountAdapter()
#
#         return {
#             'account_adapter': adapter,
#             'email_data': {
#                 'template_prefix': self.password_reset_template_prefix,
#                 'email': "h@trulii.com",
#                 'context': json.dumps(context)
#             }
#
#         }
#
#     def test_email_confirmation_task_dispatch(self):
#         task_data = self._get_email_confirmation_task_data()
#         task = SendAllAuthEmailTask()
#         result = task.apply_async((self.USER_ID,), task_data, countdown=2)
#         self.assertEqual(result.result, 'Task scheduled')
#
#     def test_remail_confirmation_task_should_been_send_on_success(self):
#         task_data = self._get_email_confirmation_task_data()
#         task = SendAllAuthEmailTask()
#         result = task.apply_async((self.USER_ID,), task_data, countdown=2)
#         email_task = EmailTaskRecord.objects.get(task_id=result.id)
#         self.assertTrue(email_task.send)
#
#     def treset_password_email_task_dispatch(self):
#         task_data = self._get_password_reset_task_data()
#         task = SendAllAuthEmailTask()
#         result = task.apply_async((self.USER_ID,), task_data, countdown=2)
#         self.assertEqual(result.result, 'Task scheduled')
#
#     def test_reset_password_email_task_should_been_send_on_success(self):
#         task_data = self._get_password_reset_task_data()
#         task = SendAllAuthEmailTask()
#         result = task.apply_async((self.USER_ID,), task_data, countdown=2)
#         email_task = EmailTaskRecord.objects.get(task_id=result.id)
#         self.assertTrue(email_task.send)
