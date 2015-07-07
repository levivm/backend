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
from users.tasks import SendAllAuthEmailTask







class CustomException(APIException):
    status_code = 400
    detail = "No tiene"

class MyAccountAdapter(DefaultAccountAdapter):


    ALLAUTH_USER_BASE_TEMPLATE= {
        'account/email/email_confirmation': "email_confirmation",
        'account/email/email_confirmation_welcome': "email_confirmation_welcome",
        'account/email/email_confirmation_signup': "email_confirmation_welcome",
        'account/email/password_reset_key': "password_reset_key",
    }



    def get_login_redirect_url(self, request):
        path = "home"
        return path


    def get_email_confirmation_redirect_url(self,request):

        path = "/email/confirm/success/"
        return path


    def send_mail(self, template_prefix, email, context):

        if template_prefix in self.ALLAUTH_USER_BASE_TEMPLATE:

            user = context['user']
            task = SendAllAuthEmailTask()
            task_data = {
                'account_adapter':self,
                'email_data':{
                    'template_prefix':template_prefix,
                    'email':email,
                    'context':context
                }

            }
            task.apply_async((user.id,),task_data, countdown=2)
        else:
            super(MyAccountAdapter, self).send_mail(template_prefix,
                                                              email,
                                                              context)