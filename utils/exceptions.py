from rest_framework.exceptions import APIException
from django.utils.translation import ugettext_lazy as _


class ServiceUnavailable(APIException):
    status_code = 503
    default_detail = str(_('Servicio temporalmente no disponible, intente luego.'))