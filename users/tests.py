import json
from rest_framework import status
from django.conf import settings
import urllib.parse
# from .views import RequestSignupViewSet
from utils.tests import BaseViewTest
from .tasks import SendEmailOrganizerConfirmationTask,SendAllAuthEmailTask
from .models import RequestSignup
from utils.models import EmailTaskRecord
from users.allauth_adapter import MyAccountAdapter
from users.views import ObtainAuthTokenView,RestFacebookLogin
from django.contrib.auth.models import User






class RestFacebookLoginTest(BaseViewTest):
    url = '/users/facebook/signup/'
    view = RestFacebookLogin

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def _get_facebook_signup_data(self):
        #TODO 
        #Este token dura dos meses, expires 6 septiembre
        #Automatizar para pedir uno nuevo
        auth_token  = "CAAWOByANCTUBABAnEZCN0CQUfmumcScZBg6dqaN7aZAHkLZBR4I3"
        auth_token += "3CTwTdUGOaYkSeLg6GKfF3x6yZB4KOlp42SF3mZBLPIMYooJAoRXd"
        auth_token += "RaMAKVohJ76GieWPyFwX93exyDSbSnI7rC1FVrD3dEFUdF3QzZBgD"
        auth_token += "7Px8LI7LyrVNLP7MqsNA1xidZC"
        return {
            'auth_token': auth_token
        }

    def test_anonymous_should_signup(self):

        client = self.client
        data   = self._get_facebook_signup_data()
        response = client.post(self.url,data=json.dumps(data),content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content,b'"token":"\w{40,40}"')

    def test_anonymous_should_login(self):
        client = self.client
        data   = self._get_facebook_signup_data()
        #signup
        client.post(self.url,data=json.dumps(data),content_type='application/json')
        
        #login
        response = client.post(self.url,data=json.dumps(data),content_type='application/json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content,b'"token":"\w{40,40}"')


class ObtainAuthTokenTest(BaseViewTest):
    url = '/api/users/token/'
    view = ObtainAuthTokenView

    def _get_signup_data(self):
        return {

            'email':'student@trulii.com',
            'first_name':'John',
            'last_name':'Messi',
            'password1':'12345678',
            'user_type':'S'
        } 


    def _get_login_data(self):
        return {
            'login':'student@trulii.com',
            'password':"12345678"
        }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()


    def test_anonymous_should_signup(self):
        client = self.client
        data   = self._get_signup_data()
        enconde_data = urllib.parse.urlencode(data)
        response = client.post(self.url,data=enconde_data,\
                            content_type='application/x-www-form-urlencoded')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content,b'"token":"\w{40,40}"')
        self.assertTrue(
            User.objects.filter(email=data['email']).exists()
        )

    def test_anonymous_should_login(self):
        client = self.client
        data   = self._get_login_data()
        signup_data   = self._get_signup_data()
        enconde_data = urllib.parse.urlencode(signup_data)
        client.post(self.url,data=enconde_data,\
                            content_type='application/x-www-form-urlencoded')
        response = client.post(self.url,data=json.dumps(data),content_type='application/json')
        expected_email_regex = bytes('"email":"%s"' % data['login'], 'utf8')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertRegexpMatches(response.content,b'"token":"\w{40,40}"')
        self.assertRegexpMatches(response.content,expected_email_regex)


class SendEmailOrganizerConfirmationAdminActionTest(BaseViewTest):
    url = '/admin/users/requestsignup/'
    REQUEST_SIGNUP_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def _get_send_verification_email_action_data(self):
        return {'action': 'send_verification_email',\
                 '_selected_action':self.REQUEST_SIGNUP_ID}

    def test_admin_send_verification_email_action(self):
        client = self.get_admin_client()
        data = self._get_send_verification_email_action_data()
        request_signup = RequestSignup.objects.get(id=self.REQUEST_SIGNUP_ID)
        self.assertFalse(request_signup.approved)
        response = client.post(self.url,data)
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
            'confirmation_id':self.CONFIRMATION_ID
        }
        result = task.apply((self.CONFIRMATION_ID, ),data,)
        self.assertEqual(result.result, 'Task scheduled')


    def test_task_should_send_on_success(self):
        task = SendEmailOrganizerConfirmationTask()
        data = {
            'confirmation_id':self.CONFIRMATION_ID
        }
        result = task.apply((self.CONFIRMATION_ID, ),data,)
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
        activate_url  = 'http://localhost:8000/users/confirm-email/'
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
            'account_adapter':adapter,
            'email_data':{
                'template_prefix':self.password_reset_template_prefix,
                'email':"h@trulii.com",
                'context':json.dumps(context)
            }

        }

    def _get_email_confirmation_task_data(self):
        context = self._get_email_confirmation_data()
        adapter = MyAccountAdapter()
        
        return {
            'account_adapter':adapter,
            'email_data':{
                'template_prefix':self.password_reset_template_prefix,
                'email':"h@trulii.com",
                'context':json.dumps(context)
            }

        }
        




    def test_email_confirmation_task_dispatch(self):
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')



    def test_remail_confirmation_task_should_been_send_on_success(self):
        
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)

    def treset_password_email_task_dispatch(self):
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')


    def test_reset_password_email_task_should_been_send_on_success(self):
        
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)