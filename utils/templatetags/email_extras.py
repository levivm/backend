from django import template

register = template.Library()

@register.filter(name='refactor_allauth_url')
def refactor_allauth_url(value):
    """Refactor django allauth urls to work with angularjs router"""
    return value.replace('users/', '')