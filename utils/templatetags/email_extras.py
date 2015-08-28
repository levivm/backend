from django import template
from django.conf import settings

register = template.Library()

@register.filter(name='refactor_allauth_url')
def refactor_allauth_url(value):
    """Refactor django allauth urls to work with angularjs router"""
    
    server_url = settings.FRONT_SERVER_URL
   	
    #server_url = "http://localhost:8080/"
    #return server_url
    rest_url   = "/".join(value.split("/")[4:])
    final_url = server_url + rest_url
    return final_url