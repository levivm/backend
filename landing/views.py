from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from users import users_constants
from .serializers import ContactFormsSerializer
from .tasks import SendContactFormEmailTask


# Create your views here.


@ensure_csrf_cookie
def landing(request):
    return render(request, 'base.html', {})


def form_modal(request):
    return render(request, 'form_modal.html', {})


class ContactFormView(APIView):
    def get(self, request, *args, **kwargs):
        contact_form_topics = [{'topic_id': k, 'topic_label': v} for k, v in users_constants.CONTACT_USER_FORM_TOPIC]
        print("Contacto Form",contact_form_topics)
        return Response(contact_form_topics, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        # contact_form_topics = users_constants.CONTACT_USER_FORM_TOPIC

        # data = request.data.copy()
        #
        # topic_index = request.data.get('topic', 2)
        # subtopic_index = request.data.get('subtopic', 0)
        #
        # topic_data = contact_form_topics[topic_index]
        # topic_name = list(contact_form_topics[topic_index].keys()).pop()
        # subtopic = topic_data[topic_name][subtopic_index]
        #
        # data['topic'] = topic_name
        # data['subtopic'] = subtopic

        form_serializer = ContactFormsSerializer(data=request.data)
        form_serializer.is_valid(raise_exception=True)
        contact_form_data = request.data
        task = SendContactFormEmailTask()
        # task.apply_async((None,), contact_form_data, countdown=2)
        task.delay(contact_form_data)
        return Response(form_serializer.data, status=status.HTTP_200_OK)
