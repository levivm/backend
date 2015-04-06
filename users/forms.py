from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings




class UserCreateForm(forms.Form):

    USER_TYPES = (
        ('O', _('Organizador')),
        ('S', _('Estudiante')),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES,
                                  required=True)

    first_name = forms.CharField(required=True)
    last_name  = forms.CharField(required=True)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.user_type  = self.cleaned_data['user_type']
        user.save()