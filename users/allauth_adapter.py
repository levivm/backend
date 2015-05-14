# -*- coding: utf-8 -*-
#"Content-Type: text/plain; charset=UTF-8\n"

from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter
from .models import OrganizerConfirmation
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseBadRequest
from rest_framework.exceptions import APIException
from django.http import Http404



class CustomException(APIException):
    status_code = 400
    detail = "No tiene"

class MyAccountAdapter(DefaultAccountAdapter):


    def get_login_redirect_url(self, request):
        path = "brow.home"
        return path


    # def save_user(self, request, sociallogin, form=None):
    #     user = super(MyAccountAdapter, self).save_user(request, sociallogin, form=form)
    #     self.login( request, user)
    #     return user

    def get_email_confirmation_redirect_url(self,request):

        path = "/email/confirm/success/"
        return path

    # def populate_username(self,request,user):
    #     raise forms.ValidationError(_("This username is already taken. Please "
    #                                   "choose another."))


    # def is_email_verified(self,request,email):
    #     user_type = request.POST.get('user_type',None) 
    #     validate = True
    #     if user_type == 'O':
    #         try:
    #             OrganizerConfirmation.objects.\
    #                 select_related('requested_signup').\
    #                 get(requested_signup__email=email)

    #         except OrganizerConfirmation.DoesNotExist:
    #             raise Http404
    #             raise CustomException(detail="No mira no pude")
    #             raise HttpResponseBadRequest(_("Este correo no tiene permiso para registro"))
    #             raise forms.ValidationError(_("This username is already taken. Please "
    #                                           "choose another."))

    #     return False