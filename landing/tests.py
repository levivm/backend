from django.conf import settings
from django.core.urlresolvers import reverse
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

    def test_post(self):
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
        pass

    def test_send_contact_form_email_task_dispatch(self):
        contact_form_data = self._get_contact_form_data()
        task = SendContactFormEmailTask()
        result = task.apply_async((None,), contact_form_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_send_contact_form_email_task_should_been_send_on_success(self):
        contact_form_data = self._get_contact_form_data()
        task = SendContactFormEmailTask()
        result = task.apply_async((None,), contact_form_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)
