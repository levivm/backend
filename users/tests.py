import json
from rest_framework import status
from django.conf import settings
# from .views import RequestSignupViewSet
from utils.tests import BaseViewTest
from .tasks import SendEmailOrganizerConfirmationTask,SendAllAuthEmailTask
from utils.models import CeleryTask
from users.allauth_adapter import MyAccountAdapter





class SendEmailOrganizerConfirmationTaskTest(BaseViewTest):
    CONFIRMATION_ID = 1

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False

    def test_task_dispatch_if_there_is_not_other_task(self):
        task = SendEmailOrganizerConfirmationTask()
        result = task.apply((self.CONFIRMATION_ID, ),)
        self.assertEqual(result.result, 'Task scheduled')


    def test_ignore_task_if_there_is_a_pending_task(self):
        task = SendEmailOrganizerConfirmationTask()
        task.apply((self.CONFIRMATION_ID, False), countdown=180)
        task2 = SendEmailOrganizerConfirmationTask()
        result = task2.apply((self.CONFIRMATION_ID, False))
        self.assertEqual(result.result, None)


    def test_task_should_delete_on_success(self):
        task = SendEmailOrganizerConfirmationTask()
        task.apply((self.CONFIRMATION_ID, ))
        self.assertEqual(CeleryTask.objects.count(), 0)


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
                'context':context
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
                'context':context
            }

        }
        

    def test_email_confirmation_task_dispatch_if_there_is_not_other_task(self):
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_email_confirmation_task_if_there_is_a_pending_task(self):
        
        task_data = self._get_email_confirmation_task_data()
        task   = SendAllAuthEmailTask()
        task.apply_async((self.USER_ID,False),task_data, countdown=180)
        task2  = SendAllAuthEmailTask()
        result = task2.apply_async((self.USER_ID,False),task_data)
        self.assertEqual(result.result, None)

    def test_remail_confirmation_task_should_delete_on_success(self):
        
        task_data = self._get_email_confirmation_task_data()
        task = SendAllAuthEmailTask()
        task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(CeleryTask.objects.count(), 0)


    def test_reset_password_email_task_dispatch_if_there_is_not_other_task(self):
        
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        result = task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_reset_password_email_ignore_task_if_there_is_a_pending_task(self):
        
        task_data = self._get_password_reset_task_data()
        task   = SendAllAuthEmailTask()
        task.apply_async((self.USER_ID,False),task_data, countdown=180)
        task2  = SendAllAuthEmailTask()
        result = task2.apply_async((self.USER_ID,False),task_data)
        self.assertEqual(result.result, None)

    def test_reset_password_email_task_should_delete_on_success(self):
        
        task_data = self._get_password_reset_task_data()
        task = SendAllAuthEmailTask()
        task.apply_async((self.USER_ID,),task_data, countdown=2)
        self.assertEqual(CeleryTask.objects.count(), 0)