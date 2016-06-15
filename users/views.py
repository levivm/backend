from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.debug import sensitive_post_parameters
from rest_framework import status
from rest_framework import viewsets
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from organizers.models import Organizer
from organizers.serializers import OrganizersSerializer
from students.models import Student
from students.serializer import StudentsSerializer
from utils.form_utils import ajax_response
from utils.forms import FileUploadForm
from .serializers import UsersSerializer


def _set_ajax_response(_super):
    form_class = _super.get_form_class()
    form = _super.get_form(form_class)
    if form.is_valid():
        response = _super.form_valid(form)
    else:
        response = _super.form_invalid(form)

    return response, form


def get_user_profile_data(user):
    try:
        profile = Organizer.objects.get(user=user)
        data = OrganizersSerializer(profile).data
    except Organizer.DoesNotExist:
        profile = Student.objects.get(user=user)
        data = StudentsSerializer(profile).data

    return data


sensitive_post_parameters_m = method_decorator(
    sensitive_post_parameters('password', 'password1', 'password2'))


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UsersSerializer

    def retrieve(self, request, *args, **kwargs):
        user = request.user

        if user.is_anonymous():
            return Response(status=status.HTTP_403_FORBIDDEN)

        data = get_user_profile_data(user)

        return Response(data)


class PhotoUploadView(APIView):
    parser_classes = (FileUploadParser, MultiPartParser)

    def post(self, request):
        user = self.request.user
        if not user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        profile = None
        data = None
        photo = None

        file_form = FileUploadForm(request.POST, request.FILES)
        if file_form.is_valid():
            photo = request.FILES['file']
        else:
            return Response(ajax_response(file_form), status=status.HTTP_406_NOT_ACCEPTABLE)

        try:
            profile = Organizer.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data = OrganizersSerializer(profile).data
        except Organizer.DoesNotExist:
            profile = Student.objects.get(user=user)
            profile.photo = photo
            profile.save()
            data = StudentsSerializer(profile).data

        return Response(data)

