import json
import urllib.parse

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from model_mommy import mommy

from rest_framework import status

from utils.tests import BaseViewTest, BaseAPITestCase
from utils.models import EmailTaskRecord
from users.allauth_adapter import MyAccountAdapter
from .models import RequestSignup
from .tasks import SendEmailOrganizerConfirmationTask, SendAllAuthEmailTask


class RestFacebookLoginTest(BaseAPITestCase):
    """
    Class to test sign up and login with Facebook
    """

    def setUp(self):
        super(RestFacebookLoginTest, self).setUp()

        # URLs
        self.facebook_signup_login_url = reverse('facebook_signup_login')

        # Objects
        mommy.make(SocialApp,
                   name='trulii',
                   client_id='1563536137193781',
                   secret='9fecd238829796fd99109283aca7d4ff',
                   provider='facebook',
                   sites=[Site.objects.get(id=settings.SITE_ID)])

    def get_signup_data(self):
        # TODO
        # Este token dura dos meses, expira 14 noviembre
        # Automatizar para pedir uno nuevo
        auth_token = "CAAWOByANCTUBAEU6rtjWRCdiv04HW7RqQnx9JVV8PWdUAlDjGn9fQh" \
                     "ZCjHM0LEaTTv1U4vjH5A23zlZCUZAdDpUMyAgsf2veZCQQf4Y5FMcFUj" \
                     "ZCLT2uNFlvCEBiTCaTcN5etZCF7xUSJlB4mqa7AZC87ZCb4amIh5QNf7" \
                     "AIbIa13y5JAdbek0Ev"
        return {'auth_token': auth_token}

    def test_signup(self):
        """
        Test to signup with Facebook
        """

        data = self.get_signup_data()

        # Anonymous should sign up
        response = self.client.post(self.facebook_signup_login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')

    def test_login(self):
        """
        Test to login with Facebook
        """

        data = self.get_signup_data()

        # signup
        self.client.post(self.facebook_signup_login_url, data)

        # login
        response = self.client.post(self.facebook_signup_login_url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')


class ObtainAuthTokenTestView(BaseAPITestCase):
    """
    Class to test sign up and login
    """
    urlencoded = {'content_type': 'application/x-www-form-urlencoded'}
    jsonencoded = {'content_type': 'application/json'}

    def setUp(self):
        super(ObtainAuthTokenTestView, self).setUp()

        # Objects
        self.password = '12345678'
        self.email = 'student@trulii.com'
        self.student.user.set_password(self.password)
        self.student.user.email = self.email
        self.student.user.save()

        # URLs
        self.signup_login_url = reverse('users:signup_login')

    def get_signup_data(self):
        return {
            'email': self.email,
            'first_name': 'John',
            'last_name': 'Messi',
            'password1': self.password,
            'user_type': 'S'
        }

    def get_login_data(self):
        return {
            'login': self.email,
            'password': self.password,
        }

    def test_signup(self):
        """
        Test to sign up an user
        """

        # Anonymous should sign up
        data = self.get_signup_data()
        response = self.client.post(self.signup_login_url, urllib.parse.urlencode(data), **self.urlencoded)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')
        self.assertTrue(User.objects.filter(email=data['email']).exists())

    def test_login(self):
        """
        Test to login an user
        """

        # Anonymous should login
        data = self.get_login_data()
        response = self.client.post(self.signup_login_url, json.dumps(data), **self.jsonencoded)
        self.assertContains(response, data['login'])
        self.assertRegexpMatches(response.content, b'"token":"\w{40,40}"')


class SendEmailOrganizerConfirmationAdminActionTest(BaseViewTest):
    url = '/admin/users/requestsignup/'
    REQUEST_SIGNUP_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def _get_send_verification_email_action_data(self):
        return {'action': 'send_verification_email', \
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


class SendEmailOrganizerConfirmationTaskTest(BaseViewTest):
    CONFIRMATION_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailOrganizerConfirmationTask()
        data = {
            'confirmation_id': self.CONFIRMATION_ID
        }
        result = task.apply((self.CONFIRMATION_ID,), data, )
        self.assertEqual(result.result, 'Task scheduled')

    def test_task_should_send_on_success(self):
        task = SendEmailOrganizerConfirmationTask()
        data = {
            'confirmation_id': self.CONFIRMATION_ID
        }
        result = task.apply((self.CONFIRMATION_ID,), data, )
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)


class SendAllAuthEmailTaskTest(BaseViewTest):
    password_reset_template_prefix = 'account/email/password_reset_key'
    email_confirmation_template_prefix = 'account/email/email_confirmation'
    USER_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def _get_reset_password_data(self):
        pass_reset_url = 'http://localhost:8000/users/password/reset/key/4-437-597e9e6b21e5adc283b2/'
        return {
            'user': self.USER_ID,
            'site': "trulii.com",
            'password_reset_url': pass_reset_url
        }

    def _get_email_confirmation_data(self):
        activate_url = 'http://localhost:8000/users/confirm-email/'
        activate_url += 'kjbps8tqbmngdk1vqub8lqlgwd6hfuznkloeh8ul2gfndalyb86kn4fswslazkzv/'
        return {
            'user': self.USER_ID,
            'key': 'kjbps8tqbmngdk1vqub8lqlgwd6hfuznkloeh8ul2gfndalyb86kn4fswslazkzv',
            'activate_url': activate_url,
            'current_site': 1
        }

    def _get_password_reset_task_data(self):
        context = self._get_reset_password_data()
        adapter = MyAccountAdapter()

        return {
            'account_adapter': adapter,
            'email_data': {
                'template_prefix': self.password_reset_template_prefix,
                'email': "h@trulii.com",
                'context': json.dumps(context)
            }

        }

    def _get_email_confirmation_task_data(self):
        context = self._get_email_confirmation_data()
        adapter = MyAccountAdapter()

        return {
            'account_adapter': adapter,
            'email_data': {
                'template_prefix': self.password_reset_template_prefix,
                'email': "h@trulii.com",
                'context': json.dumps(context)
            }

        }

    def test_email_confirmation_task_dispatch(self):
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,), task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_remail_confirmation_task_should_been_send_on_success(self):
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,), task_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)

    def treset_password_email_task_dispatch(self):
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,), task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_reset_password_email_task_should_been_send_on_success(self):
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,), task_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
