import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import now
from model_mommy import mommy
from rest_framework import status
from rest_framework.test import APITestCase

from locations.factories import CityFactory
from locations.models import City
from users.models import OrganizerConfirmation
from utils.models import EmailTaskRecord
from utils.tests import BaseViewTest, BaseAPITestCase
from .models import RequestSignup
from .tasks import SendEmailOrganizerConfirmationTask


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

    def _get_send_verification_email_action_data(self):
        return {'action': 'send_verification_email',
                '_selected_action': self.REQUEST_SIGNUP_ID}

    @mock.patch('users.tasks.SendEmailOrganizerConfirmationTask.apply_async')
    def test_admin_send_verification_email_action(self, apply_async):
        client = self.get_admin_client()
        data = self._get_send_verification_email_action_data()
        request_signup = RequestSignup.objects.get(id=self.REQUEST_SIGNUP_ID)
        self.assertFalse(request_signup.approved)
        response = client.post(self.url, data)
        request_signup = RequestSignup.objects.get(id=self.REQUEST_SIGNUP_ID)
        self.assertTrue(request_signup.approved)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)


class SendEmailOrganizerConfirmationTaskTest(APITestCase):
    def setUp(self):
        self.confirmation = mommy.make(OrganizerConfirmation, requested_signup__city=CityFactory())

    @mock.patch('users.tasks.now')
    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_success(self, send_mail, date_now):
        """
        Test case when it's success
        """

        send_mail.return_value = [{
            'email': self.confirmation.requested_signup.email,
            'status': 'sent',
            'reject_reason': None
        }]

        today = now()
        date_now.return_value = today

        task = SendEmailOrganizerConfirmationTask()
        task_id = task.delay(self.confirmation.id)

        context = {
            'activate_url': self.confirmation.get_confirmation_url(),
        }

        self.assertTrue(EmailTaskRecord.objects.filter(
            task_id=task_id,
            to=self.confirmation.requested_signup.email,
            status='sent',
            data=context,
            template_name='authentication/email/request_signup_confirmation.html').exists())

        confirmation = OrganizerConfirmation.objects.get(id=self.confirmation.id)
        self.assertEqual(confirmation.sent, today)
