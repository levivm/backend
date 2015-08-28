import json
from rest_framework import status
from utils.tests import BaseViewTest
from utils.models import EmailTaskRecord
from .views import ContactFormView
from django.conf import settings
from .tasks import SendContactFormEmailTask



# class SendContactFormEmailTaskTest(BaseViewTest):
# 

class ContactFormTest(BaseViewTest):
    url = '/api/contact-us/'
    view = ContactFormView



    def _get_contact_form_data(self):
        return {
            "topic":0,
            "subtopic":1,
            "name":"Levi",
            "email":"truli@gmail.com",
            "phone_number":"222222",
            "description":"hola soy una description",
            "city":"Bogota"
            }

    def test_url_resolve_to_view_correctly(self):
        self.url_resolve_to_view_correctly()

    def test_get_contact_form_topics(self):
        contact_form_topic = b"Tengo una pregunta sobre inscribirme en una actividad"
        self.method_get_should_return_data(clients=self.client,response_data=contact_form_topic)

    def test_anyone_can_submit_contact_form(self):
        client = self.get_organizer_client()
        data     = json.dumps(self._get_contact_form_data())
        response = client.post(self.url,data=data,content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


    def test_submit_contact_form_error_if_there_is_not_required_data(self):
        client = self.get_organizer_client()
        data     = json.dumps({'name':'Levi'})
        response = client.post(self.url,data=data,content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class SendContactFormEmailTaskTest(BaseViewTest):

    def _get_contact_form_data(self):
        return {
            "topic":0,
            "subtopic":1,
            "name":"Levi",
            "email":"truli@gmail.com",
            "phone_number":"222222",
            "description":"hola soy una description",
            "city":"Bogota"
            }

    def setUp(self):
        settings.CELERY_ALWAYS_EAGER = True
    def tearDown(self):
        settings.CELERY_ALWAYS_EAGER = False


    def test_send_contact_form_email_task_dispatch(self):
        contact_form_data = self._get_contact_form_data()
        task = SendContactFormEmailTask()
        result = task.apply_async((None,),contact_form_data, countdown=2)
        self.assertEqual(result.result, 'Task scheduled')

    def test_send_contact_form_email_task_should_been_send_on_success(self):
        
        contact_form_data = self._get_contact_form_data()
        task = SendContactFormEmailTask()
        result = task.apply_async((None,),contact_form_data, countdown=2)
        email_task = EmailTaskRecord.objects.get(task_id=result.id)
        self.assertTrue(email_task.send)


