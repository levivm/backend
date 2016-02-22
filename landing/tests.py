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

        settings.CELERY_ALWAYS_EAGER = True

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
            "email": "truli@gmail.com",
            "phone_number": "222222",
            "description": "hola soy una description",
            "city": "Bogota"
        }

    def setUp(self):
        self.email = 'contact@trulii.com'

    @mock.patch('utils.mixins.mandrill.Messages.send')
    def test_run(self, send_mail):
        """
        Test that the task sends the email
        """

        send_mail.return_value = [{
            '_id': '042a8219744b4b40998282fcd50e678e',
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
                status='sent').exists())

        message = {
            'from_email': 'contacto@trulii.com',
            'html': loader.get_template('landing/email/contact_us_form_message.txt').render(),
            'subject': 'Subject contact form',
            'to': [{'email': self.email}],
            'merge_vars': [],
            'global_merge_vars': [{'name': k, 'content': v} for k, v in contact_form_data.items()],
        }

        called_message = send_mail.call_args[1]['message']

        self.assertTrue(all(item in called_message.items() for item in message.items()))
