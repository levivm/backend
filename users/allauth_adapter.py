from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):

    def get_email_confirmation_redirect_url(self,request):
        path = "/email/confirm/success/"
        return path