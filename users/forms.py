from django import forms
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from .models import OrganizerConfirmation


class UserCreateForm(forms.Form):

    USER_TYPES = (
        ('O', _('Organizador')),
        ('S', _('Estudiante')),
    )

    user_type = forms.ChoiceField(choices=USER_TYPES,
                                  required=True)

    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)

    def clean_first_name(self):
        data = self.cleaned_data
        user_type = data['user_type']
        first_name = data.get('first_name')

        if user_type == settings.STUDENT_TYPE:
            if not first_name:
                raise forms.ValidationError(_("Este campo es requerido"))

        return first_name

    def clean_email(self):
        data = self.cleaned_data
        email = data.get('email')
        return email


    def clean_last_name(self):
        data = self.cleaned_data
        user_type = data['user_type']
        last_name = data.get('last_name')

        if user_type == settings.STUDENT_TYPE:
            if not data.get('last_name'):
                raise forms.ValidationError(_("Este campo es requerido")) 

        return last_name

    def clean(self):
        data = self.cleaned_data
        user_type = data['user_type']


        email = data.get('email')

        if user_type == settings.ORGANIZER_TYPE:
            oc = OrganizerConfirmation.objects.\
                select_related('requested_signup').\
                filter(requested_signup__email=email).count()

            if not oc:
                msg = _("Este correo no ha sido previamente validado")
                raise forms.ValidationError(msg) 

            return data

        return data


    def signup(self, request, user):

        user.first_name = self.cleaned_data['first_name']
        user.last_name  = self.cleaned_data['last_name']
        user.user_type  = self.cleaned_data['user_type']

        if user.user_type == settings.ORGANIZER_TYPE:

            email = self.cleaned_data['email']
            ocs = OrganizerConfirmation.objects.\
                    select_related('requested_signup').\
                    filter(requested_signup__email=email)

            ocs.update(used=True)

        user.save()