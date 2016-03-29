import mock
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import loader
from rest_framework import status
from rest_framework.test import APITestCase

from users import users_constants
from utils.models import EmailTaskRecord
from utils.tests import BaseViewTest, BaseAPITestCase
from .tasks import SendContactFormEmailTask


class ContactFormTest(BaseAPITestCase):
    """
    Testing cases for ContactForm
    """

    def setUp(self):
        self.contact_url = reverse('contact_form')
        self.data = {
            "topic": "suggestion",
            "name": "Levi",
            "email": "truli@gmail.com",
            "phone_number": "222222",
            "description": "hola soy una description",
            "city": "Bogota"
        }

    def test_get(self):
        """
        Test the topics
        """

        content = [{'topic_id': k, 'topic_label': v} for k, v in users_constants.CONTACT_USER_FORM_TOPIC]

        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item in response.data for item in content))

    @mock.patch('landing.tasks.SendContactFormEmailTask.delay')
    def test_post(self, delay):
        """
        Test the post of contact form
        """

        response = self.client.post(self.contact_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_error(self):
        """
        Test fields required
        """

        response = self.client.post(self.contact_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class SendContactFormEmailTaskTest(APITestCase):
    def _get_contact_form_data(self):
        return {
            "topic": "suggestion",
            "name": "Levi",
            "email": "trulii@gmail.com",
            "phone_number": "222222",
            "description": "hola soy una description",
            "city": "Bogota"
        }

    def setUp(self):
        self.email = 'contact@trulii.com'

    @mock.patch('utils.tasks.SendEmailTaskMixin.send_mail')
    def test_run(self, send_mail):
        """
        Test that the task sends the email
        """

        send_mail.return_value = [{
            'email': self.email,
            'status': 'sent',
            'reject_reason': None
        }]

        contact_form_data = self._get_contact_form_data()

        task = SendContactFormEmailTask()
        task_id = task.delay(contact_form_data)

        self.assertTrue(EmailTaskRecord.objects.filter(
                task_id=task_id,
                to=self.email,
                status='sent',
                data=contact_form_data,
                template_name='landing/email/contact_us.html').exists())
